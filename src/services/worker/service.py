import asyncio
import logging
import typing
from functools import cached_property

import grpc
from google.protobuf import empty_pb2, wrappers_pb2

from src.common.rpc import (
    common_pb2,
    dispatcher_pb2_grpc,
    nameserver_pb2,
    nameserver_pb2_grpc,
    worker_pb2_grpc,
)
from src.services import DISPATCHER_NAME
from src.services.worker.tasks import (
    HashTaskDispatcher,
    ReverseTaskDispatcher,
    SumTaskDispatcher,
    TaskDispatcher,
)

logger = logging.getLogger()


class WorkerServicer(worker_pb2_grpc.WorkerServicer):
    def __init__(self, task_type: str, server_address: str, name_service_address: str):
        self.server_address = server_address
        self.name_service_address = name_service_address

        task_workers: typing.Final[dict[str, TaskDispatcher]] = {
            "sum": SumTaskDispatcher(),
            "hash": HashTaskDispatcher(hash),
            "reverse": ReverseTaskDispatcher(),
        }

        self.task_type = task_type
        self.task_worker = task_workers[self.task_type]

        logger.info("Started worker with task type %s", self.task_type)

        self._registered = False
        self.register_at_name_server()

    def __del__(self):
        self.unregister_at_name_server()

    def receive_task(self, request: common_pb2.Task, context: grpc.ServicerContext):
        """DISPATCHER -> WORKER: Queue a new task for processing on the worker"""
        logger.info("Execution of task was requested")
        asyncio.get_running_loop().run_until_complete(self.execute_task(request))
        return empty_pb2.Empty()

    def get_status(self, request, context):
        """Any -> WORKER: Query the status of the worker"""
        logger.info("Status was requested")
        return self.task_worker.get_status()

    async def execute_task(self, request: common_pb2.Task):
        valid, result = self.task_worker.process_task(request.payload)

        with grpc.insecure_channel(self.dispatcher_address) as channel:
            stub = dispatcher_pb2_grpc.DispatchStub(channel)
            # This should not fail, but if it does, we want to just raise the error
            stub.return_result(
                common_pb2.TaskResult(
                    task_id=request.task_id, payload=result, valid=valid
                )
            )
            logger.info("Sent task result to dispatcher")

    @cached_property
    def dispatcher_address(self):
        with grpc.insecure_channel(self.name_service_address) as channel:
            try:
                stub = nameserver_pb2_grpc.NameServiceStub(channel)
                address: common_pb2.ServiceIPWithPort = stub.lookup(DISPATCHER_NAME)

                ip, port = address.ip, address.port
                return f"{ip}:{port}"
            except grpc.RpcError:
                raise KeyError("Dispatcher service could not be found")

    def register_at_name_server(self):
        if self._registered:
            return

        with grpc.insecure_channel(self.name_service_address) as channel:
            stub = nameserver_pb2_grpc.NameServiceStub(channel)
            _ = stub.register(
                nameserver_pb2.Service(
                    name=self.task_type,
                    address=common_pb2.ServiceIPWithPort(
                        ip=self.server_address.rsplit(":", 1)[0],
                        port=int(self.server_address.rsplit(":", 1)[1]),
                    ),
                )
            )

        self._registered = True
        logger.info(
            "Registered self with address %s and name %s at the name server",
            self.server_address,
            self.task_type,
        )

    def unregister_at_name_server(self):
        if not self._registered:
            return

        with grpc.insecure_channel(self.name_service_address) as channel:
            stub = nameserver_pb2_grpc.NameServiceStub(channel)
            _ = stub.unregister(wrappers_pb2.StringValue(value=self.task_type))

        self._registered = False
        logger.info(
            "Unregistered self with address %s and name %s at the name server",
            self.server_address,
            self.task_type,
        )
