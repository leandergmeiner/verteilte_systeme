from src.common.rpc.services import nameserver_pb2_grpc
from src.common.rpc.types import nameserver_pb2, common_pb2
import grpc
from grpc_status import rpc_status
import ipaddress
from google.protobuf import wrappers_pb2
from google.rpc import status_pb2


class NameServiceServicer(nameserver_pb2_grpc.NameServiceServicer):
    def __init__(self):
        self.name_address_lookup: dict[
            str, tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, int]
        ] = {}

    def validate_name(self, name: str):
        if not name.isascii():
            return False, "INVALID_SERVICE_NAME"
        return True, None

    def validate_address(
        self, ip: str, port: int
    ) -> tuple[
        tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, int] | None,
        bool,
        str | None,
    ]:
        try:
            _ = ipaddress.ip_address(ip)
        except ValueError:
            msg = "INVALID_IP_ADDRESS"
            return None, False, msg

        if port >= 2**16:
            msg = "INVALID_PORT"
            return None, False, msg

        return (ip, port), True, None

    def register(self, request: nameserver_pb2.Service, context: grpc.ServicerContext):
        name, ip, port = request.name, request.address.ip, request.address.port
        valid, msg = self.validate_name(name)
        if not valid:
            context.abort_with_status(
                rpc_status.to_status(
                    status_pb2.Status(grpc.StatusCode.INVALID_ARGUMENT, msg)
                )
            )
        if name in self.name_address_lookup:
            msg = 'ALREADY_REGISTERED'
            context.abort_with_status(
                rpc_status.to_status(
                    status_pb2.Status(grpc.StatusCode.ALREADY_EXISTS, msg)
                )
            )

        address, valid, msg = self.validate_address(ip, port)
        if not valid:
            context.abort_with_status(
                rpc_status.to_status(
                    status_pb2.Status(grpc.StatusCode.INVALID_ARGUMENT, msg)
                )
            )

        self.name_address_lookup[name] = address

    def unregister(
        self, request: wrappers_pb2.StringValue, context: grpc.ServicerContext
    ):
        name = request.value

        # Fail silently if service is unknown
        if name in self.name_address_lookup:
            del self.name_address_lookup[name]

    def lookup(self, request: wrappers_pb2.StringValue, context: grpc.ServicerContext):
        name = request.value
        if name not in self.name_address_lookup:
            msg = "UNKNOWN_SERVICE"
            context.abort_with_status(
                rpc_status.to_status(status_pb2.Status(grpc.StatusCode.NOT_FOUND, msg))
            )

        ip, port = self.name_address_lookup[name]
        return common_pb2.ServiceIPWithPort(ip, port)
