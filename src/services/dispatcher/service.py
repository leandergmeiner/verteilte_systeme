import logging
import time
import typing
from queue import SimpleQueue

import grpc
from google.protobuf import empty_pb2, wrappers_pb2
from google.rpc import code_pb2, status_pb2
from grpc_status import rpc_status

from src.common.rpc import (
    common_pb2,
    dispatcher_pb2_grpc,
    nameserver_pb2,
    nameserver_pb2_grpc,
    worker_pb2_grpc,
)
from src.services import DISPATCHER_NAME

logger = logging.getLogger()


class DispatcherService(dispatcher_pb2_grpc.DispatchServicer):
    def __init__(self, server_address: str, name_service_address: str):
        super().__init__()

        self.server_address = server_address
        self.name_service_address = name_service_address

        logging.info(
            "Dispacher started. Name server address is %s", self.name_service_address
        )

        self._next_task_id = 0
        self.task_queue = SimpleQueue()
        self.results: dict[int, typing.Iterable] = {}

        self._registered = False
        self.register_at_name_server()

    def __del__(self):
        self.unregister_at_name_server()

    def execute(
        self, request: common_pb2.ExecuteTaskRequest, context: grpc.ServicerContext
    ):
        """CLIENT -> DISPATCHER: Client requests execution of task"""
        task_id = self.next_task_id()
        task = common_pb2.Task(task_id=task_id, payload=request.payload)

        status, address = self.lookup_worker(request.type)
        if status.code != code_pb2.OK:
            context.abort_with_status(rpc_status.to_status(status))

        assert address is not None

        ip, port = address.ip, address.port
        logger.info(
            "Dispatching task of type %s to worker %s", request.type, f"{ip}:{port}"
        )

        status = self.dispatch_task_to_worker(address, task)

        if status.code != code_pb2.OK:
            context.abort_with_status(rpc_status.to_status(status))

        return wrappers_pb2.UInt32Value(value=task.task_id)

    def get_task_result(
        self, request: wrappers_pb2.UInt32Value, context: grpc.ServicerContext
    ):
        """CLIENT -> DISPATCHER: Client requests result from Dispatcher for task"""
        task_id = request.value

        if task_id not in self.results:
            context.abort_with_status(
                rpc_status.to_status(
                    status_pb2.Status(
                        code=code_pb2.NOT_FOUND, message="UNKNOWN_TASK_ID"
                    )
                )
            )

        logger.info("A client requested result of task %i.", task_id)
        result = common_pb2.TaskResult(task_id=task_id, payload=self.results[task_id])
        del self.results[task_id]

        return result

    def return_result(self, request: common_pb2.Task, context: grpc.ServicerContext):
        """WORKER -> DISPATCH: Returns result of computation"""
        status = self.store_result(request)
        if status.code != code_pb2.OK:
            context.abort_with_status(rpc_status.to_status(status))

        logger.info("A worker returned the result of task %i.", request.task_id)

        return empty_pb2.Empty()

    def dispatch_task_to_worker(
        self, address: common_pb2.ServiceIPWithPort, task: common_pb2.Task
    ) -> status_pb2.Status:
        ip, port = address.ip, address.port
        addr = f"{ip}:{port}"
        with grpc.insecure_channel(addr) as channel:
            try:
                stub = worker_pb2_grpc.WorkerStub(channel)
                stub.receive_task(task)

                return status_pb2.Status(code=code_pb2.OK)
            except grpc.RpcError:
                return status_pb2.Status(
                    code=code_pb2.UNKNOWN, message="WORKER_RECEIVE_TASK_FAILED"
                )
            except Exception:
                return status_pb2.Status(code=code_pb2.UNKNOWN)

    def lookup_worker(
        self, type: str
    ) -> tuple[status_pb2.Status, common_pb2.ServiceIPWithPort | None]:
        with grpc.insecure_channel(self.name_service_address) as channel:
            try:
                stub = nameserver_pb2_grpc.NameServiceStub(channel)
                address: common_pb2.ServiceIPWithPort = stub.lookup(
                    wrappers_pb2.StringValue(value=type)
                )

                return status_pb2.Status(code=code_pb2.OK), address
            except grpc.RpcError:
                return status_pb2.Status(
                    code=code_pb2.NOT_FOUND, message="WORKER_LOOKUP_FAILED"
                ), None

    def store_result(self, task_result: common_pb2.Task) -> status_pb2.Status:
        if task_result.task_id in self.results:
            return status_pb2.Status(
                code=code_pb2.ALREADY_EXISTS, message="RESULT_ALREADY_RECEIVED"
            )

        self.results[task_result.task_id] = task_result.payload
        return status_pb2.Status(code=code_pb2.OK)

    def next_task_id(self) -> int:
        self._next_task_id += 1
        return self._next_task_id

    def register_at_name_server(self):
        if self._registered:
            return

        with grpc.insecure_channel(self.name_service_address) as channel:
            while True:
                try:
                    stub = nameserver_pb2_grpc.NameServiceStub(channel)
                    _ = stub.register(
                        nameserver_pb2.Service(
                            name=DISPATCHER_NAME,
                            address=common_pb2.ServiceIPWithPort(
                                ip=self.server_address.rsplit(":")[0],
                                port=int(self.server_address.rsplit(":")[1]),
                            ),
                        )
                    )
                    break
                except grpc.RpcError as e:
                    logger.warning(
                        "Could not register at the name server. The error was \"%s\"",
                        e.details(),
                    )
                    logger.warning("Trying again ...")
                    time.sleep(3.0)
                    continue

        self._registered = True
        logger.info(
            "Registered self with address %s and name %s at the name server",
            self.server_address,
            DISPATCHER_NAME,
        )

    def unregister_at_name_server(self):
        if not self._registered:
            return

        with grpc.insecure_channel(self.name_service_address) as channel:
            try:
                stub = nameserver_pb2_grpc.NameServiceStub(channel)
                _ = stub.unregister(wrappers_pb2.StringValue(value=DISPATCHER_NAME))
                self._registered = False
                logger.info(
                    "Unegistered self with address %s and name %s at the name server",
                    self.server_address,
                    DISPATCHER_NAME,
                )
            except grpc.RpcError:
                logger.warning("Could not unregister from the name server.")

