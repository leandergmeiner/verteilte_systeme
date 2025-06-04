import logging
from concurrent import futures

import grpc

from src.services.nameserver.service import NameServiceServicer, nameserver_pb2_grpc

logger = logging.getLogger()


def create_server(server_address: str = "[::]:50051"):
    server = grpc.server(futures.ThreadPoolExecutor())
    nameserver_pb2_grpc.add_NameServiceServicer_to_server(NameServiceServicer(), server)
    _port = server.add_insecure_port(server_address)
    server.start()
    logger.info("Started NameServer, waiting for connections.")
    server.wait_for_termination()
