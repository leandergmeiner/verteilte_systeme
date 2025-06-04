import ipaddress
import logging

import grpc
from google.protobuf import wrappers_pb2, empty_pb2
from google.rpc import code_pb2, status_pb2
from grpc_status import rpc_status

from src.common.rpc import common_pb2, nameserver_pb2, nameserver_pb2_grpc

logger = logging.getLogger()

logger = logging.getLogger()


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
        # try:
        #     _ = ipaddress.ip_address(ip)
        # except ValueError:
        #     msg = "INVALID_IP_ADDRESS"
        #     return None, False, msg

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
                    status_pb2.Status(code=code_pb2.INVALID_ARGUMENT, message=msg)
                )
            )
            
        if name in self.name_address_lookup:
            msg = "ALREADY_REGISTERED"
            context.abort_with_status(
                rpc_status.to_status(
                    status_pb2.Status(code=code_pb2.ALREADY_EXISTS, message=msg)
                )
            )

        address, valid, msg = self.validate_address(ip, port)
        if not valid:
            context.abort_with_status(
                rpc_status.to_status(
                    status_pb2.Status(code=code_pb2.INVALID_ARGUMENT, message=msg)
                )
            )

        logger.info(
            "The service worker %s with the type %s has been registered.",
            str(ip) + str(port),
            name,
        )

        logger.info(
            "The service worker %s with the type %s has been registered.",
            f"{ip}:{port}",
            name,
        )

        self.name_address_lookup[name] = address

        return empty_pb2.Empty()

    def unregister(
        self, request: wrappers_pb2.StringValue, context: grpc.ServicerContext
    ):
        name = request.value

        # Fail silently if service is unknown
        if name in self.name_address_lookup:
            del self.name_address_lookup[name]
            logger.info("Unregistered service worker of type %s.", name)

        return empty_pb2.Empty()

    def lookup(self, request: wrappers_pb2.StringValue, context: grpc.ServicerContext):
        name = request.value

        if name not in self.name_address_lookup:
            msg = "UNKNOWN_SERVICE"
            context.abort_with_status(
                rpc_status.to_status(
                    status_pb2.Status(code=code_pb2.NOT_FOUND, message=msg)
                )
            )

        logger.info(
            "The address for the service worker of type %s has been requested.", name
        )

        ip, port = self.name_address_lookup[name]
        return common_pb2.ServiceIPWithPort(ip=ip, port=port)
