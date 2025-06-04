import logging
import os
from concurrent import futures

import grpc

from src.services.dispatcher.service import DispatcherService, dispatcher_pb2_grpc

logger = logging.getLogger()


def create_server(
    name_server_address: str | None = "[::]:50051", server_address: str = "[::]:50052"
):
    name_server_address = name_server_address or os.environ.get("NAME_SERVICE")

    if name_server_address is None:
        raise ValueError("Unknown name service address.")

    server = grpc.server(futures.ThreadPoolExecutor())
    dispatcher_pb2_grpc.add_DispatchServicer_to_server(
        DispatcherService(name_server_address), server
    )
    _port = server.add_insecure_port(server_address)
    server.start()
    logger.info("Started Dispatcher, waiting for connections.")
    server.wait_for_termination()
