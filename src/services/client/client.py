import grpc
from src.services import DISPATCHER_NAME
from src.common.rpc import nameserver_pb2_grpc, common_pb2, dispatcher_pb2_grpc
from google.protobuf import wrappers_pb2


def get_dispatcher_address(name_service_address: str):
    with grpc.insecure_channel(name_service_address) as channel:
        try:
            stub = nameserver_pb2_grpc.NameServiceStub(channel)
            address: common_pb2.ServiceIPWithPort = stub.lookup(
                wrappers_pb2.StringValue(value=DISPATCHER_NAME)
            )

            ip, port = address.ip, address.port
            return f"{ip}:{port}"
        except grpc.RpcError:
            raise KeyError("Dispatcher service could not be found")


def execute_command(command: str, *args: str, name_service_address: str = "[::]:50051"):
    args = map(str, args)

    dispatcher_address = get_dispatcher_address(name_service_address)
    with grpc.insecure_channel(dispatcher_address) as channel:
        stub = dispatcher_pb2_grpc.DispatchStub(channel)
        task_request = common_pb2.ExecuteTaskRequest(type=command, payload=args)
        task_id: wrappers_pb2.UInt32Value = stub.execute(task_request)

        while True:  # Poll for results
            try:
                results: common_pb2.TaskResult = stub.get_task_result(task_id)
                print("Result: ", " ".join(results.payload))

                break
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:  # Resource is not yet available
                    print("Got here")
                    continue
                else:
                    print(e.message())
