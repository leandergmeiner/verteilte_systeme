import logging
from concurrent import futures

import grpc

from src.services.nameserver.service import NameServiceServicer, nameserver_pb2_grpc

logger = logging.getLogger()


def create_server(server_address: str = "0.0.0.0:50051"):
    server = grpc.server(futures.ThreadPoolExecutor())
    nameserver_pb2_grpc.add_NameServiceServicer_to_server(NameServiceServicer(), server)
    _port = server.add_insecure_port(server_address)
    try:
        server.start()
        logger.info("Started NameServer, waiting for connections.")
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt, shutting down ...")
        server.stop(1.)
