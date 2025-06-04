import logging
from queue import SimpleQueue

import grpc
from google.protobuf import any_pb2, empty_pb2, wrappers_pb2
from google.rpc import status_pb2
from grpc_status import rpc_status

from src.common.rpc import (
    common_pb2,
    dispatcher_pb2_grpc,
    nameserver_pb2_grpc,
    worker_pb2_grpc,
)

logger = logging.getLogger()


class DispatcherService(dispatcher_pb2_grpc.DispatchServicer):
    def __init__(self, name_service_address: str):
        super().__init__()

        self.name_service_address = name_service_address

        logging.info(
            "Dispacher startet. Name server address is %s", self.name_service_address
        )

        self._next_task_id = 0
        self.task_queue = SimpleQueue()
        self.results: dict[int, any_pb2.Any] = {}

    def execute(
        self, request: common_pb2.ExecuteTaskRequest, context: grpc.ServicerContext
    ):
        """CLIENT -> DISPATCHER: Client requests execution of task"""
        # TODO: store_result
        task_id = self.next_task_id()
        task = common_pb2.Task(task_id, request.payload)

        status, address = self.lookup_worker(request.type)
        if status.code != grpc.StatusCode.OK:
            context.abort_with_status(rpc_status.to_status(status))

        assert address is not None

        logger.info(
            "Dispatching task of type %s to worker %s",
            request.type,
            str(address.ip) + str(address.port),
        )

        status = self.dispatch_task_to_worker(address, task)

        if status.code != grpc.StatusCode.OK:
            context.abort_with_status(rpc_status.to_status(status))

        return empty_pb2.Empty()

    def get_task_result(
        self, request: wrappers_pb2.UInt32Value, context: grpc.ServicerContext
    ):
        """CLIENT -> DISPATCHER: Client requests result from Dispatcher for task"""
        task_id = request.value

        if task_id not in self.results:
            context.abort_with_status(
                rpc_status.to_status(
                    status_pb2.Status(grpc.StatusCode.NOT_FOUND, "UNKNOWN_TASK_ID")
                )
            )

        logger.info("A client requested result of task %i.", task_id)

        result: any_pb2.Any = self.results[task_id]
        return result

    def return_result(self, request: common_pb2.Task, context: grpc.ServicerContext):
        """WORKER -> DISPATCH: Returns result of computation"""
        status = self.store_result(request)
        if status.code != grpc.StatusCode.OK:
            context.abort_with_status(rpc_status.to_status(status))

        logger.info("A worker returned the result of task %i.", request.task_id)

        return empty_pb2.Empty()

    def dispatch_task_to_worker(
        self, address: common_pb2.ServiceIPWithPort, task: common_pb2.Task
    ) -> status_pb2.Status:
        addr = str(address.ip) + str(address.port)
        with grpc.insecure_channel(addr) as channel:
            try:
                stub = worker_pb2_grpc.WorkerStub(channel)
                stub.receive_task(task)

                return status_pb2.Status(grpc.StatusCode.OK)
            except grpc.RpcError as e:
                return e.status()
            except Exception:
                return status_pb2.Status(grpc.StatusCode.UNKNOWN)

    def lookup_worker(
        self, type: str
    ) -> tuple[status_pb2.Status, common_pb2.ServiceIPWithPort | None]:
        with grpc.insecure_channel(self.name_service_address) as channel:
            try:
                stub = nameserver_pb2_grpc.NameServiceStub(channel)
                address: common_pb2.ServiceIPWithPort = stub.lookup(type)

                return status_pb2.Status(grpc.StatusCode.OK), address
            except grpc.RpcError as e:
                return e.status(), None

    def store_result(self, task_result: common_pb2.Task) -> status_pb2.Status:
        if task_result.task_id in self.results:
            return status_pb2.Status(
                grpc.StatusCode.ALREADY_EXISTS, "RESULT_ALREADY_RECEIVED"
            )

        self.results[task_result.task_id] = task_result.payload
        return status_pb2.Status(grpc.StatusCode.OK)

    def next_task_id(self) -> int:
        self._next_task_id += 1
        return self._next_task_id
