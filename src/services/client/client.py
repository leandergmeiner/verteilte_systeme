import logging
import os

import grpc
from google.protobuf import empty_pb2, wrappers_pb2

from src.common.rpc import (
    common_pb2,
    dispatcher_pb2_grpc,
    nameserver_pb2_grpc,
    worker_pb2,
    worker_pb2_grpc,
)
from src.services import DISPATCHER_NAME

logger = logging.getLogger("client")

def get_servicer_address(name_service_address: str, service_type: str):
    with grpc.insecure_channel(name_service_address) as channel:
        try:
            stub = nameserver_pb2_grpc.NameServiceStub(channel)
            address: common_pb2.ServiceIPWithPort = stub.lookup(
                wrappers_pb2.StringValue(value=service_type)
            )

            ip, port = address.ip, address.port
            return f"{ip}:{port}"
        except grpc.RpcError:
            raise KeyError("Dispatcher service could not be found")


def execute_command(command: str, *args: str, name_service_address: str = "localhost:50051"):
    log_file = f"/logs/client-{command}-log.txt"
    # Delete old logs
    if os.path.exists(log_file):
        os.remove(log_file)

    logging.basicConfig(level=logging.INFO,
                        filename=log_file,
                        filemode="a",
                        )

    args = map(str, args)

    dispatcher_address = get_servicer_address(name_service_address, DISPATCHER_NAME)
    with grpc.insecure_channel(dispatcher_address) as channel:
        try:
            stub = dispatcher_pb2_grpc.DispatchStub(channel)
            task_request = common_pb2.ExecuteTaskRequest(type=command, payload=args)
            task_id: wrappers_pb2.UInt32Value = stub.execute(task_request)
        except grpc.RpcError as e:
            logger.info("Executing the task failed with message: %s", e.details())
            return

        while True:  # Poll for results
            try:
                results: common_pb2.TaskResult = stub.get_task_result(task_id)
                logger.info("Result: %s", " ".join(results.payload))
                break
            except grpc.RpcError as e:
                if (
                    e.code() == grpc.StatusCode.NOT_FOUND
                ):  # Resource is not yet available
                    continue
                else:
                    logger.warning(
                        f"Retrieving result of task {task_id} failed with message: %s",
                        e.details(),
                    )
                    return


def worker_help(command: str, name_service_address: str = "localhost:50051"):
    worker_address = get_servicer_address(name_service_address, command)

    with grpc.insecure_channel(worker_address) as channel:
        stub = worker_pb2_grpc.WorkerStub(channel)
        status: worker_pb2.WorkerStatus = stub.get_status(empty_pb2.Empty())
        print(status.usage)
