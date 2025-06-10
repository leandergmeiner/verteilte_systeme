import logging
import os
from concurrent import futures

import grpc

from src.services.dispatcher.service import DispatcherService, dispatcher_pb2_grpc

logger = logging.getLogger()


def create_server(
    name_server_address: str | None = "0.0.0.0:50051",
    server_address: str = "0.0.0.0:50052",
    registered_server_address: str = "", # Server address given to the nameserver during registration
):
    name_server_address = name_server_address or os.environ.get("NAME_SERVICE")

    # if the server address to register to the name server does not differ it should be equal to the server address
    if not registered_server_address:
        registered_server_address = server_address

    if name_server_address is None:
        raise ValueError("Unknown name service address.")

    server = grpc.server(futures.ThreadPoolExecutor())
    dispatcher_pb2_grpc.add_DispatchServicer_to_server(
        DispatcherService(registered_server_address, name_server_address), server
    )
    _port = server.add_insecure_port(server_address)
    try:
        server.start()
        logger.info("Started Dispatcher, waiting for connections.")
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt, shutting down ...")
        server.stop(1.)
