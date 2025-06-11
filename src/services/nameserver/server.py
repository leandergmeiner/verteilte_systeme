import logging
import os
import sys
from concurrent import futures
from pathlib import Path

import grpc

from src.services.nameserver.service import NameServiceServicer, nameserver_pb2_grpc

logger = logging.getLogger()


def create_server(server_address: str = "0.0.0.0:50051", log_dir: str = None):
    log_dir = log_dir or "logs"
    log_file = Path(log_dir, "nameserver-log.txt")
    # Delete old logs
    if os.path.exists(log_file):
        os.remove(log_file)

    logging.basicConfig(level=logging.INFO, filename=log_file, filemode="a")
    logger.addHandler(logging.StreamHandler(sys.stdout))

    server = grpc.server(futures.ThreadPoolExecutor())
    nameserver_pb2_grpc.add_NameServiceServicer_to_server(NameServiceServicer(), server)
    _port = server.add_insecure_port(server_address)
    try:
        server.start()
        logger.info("Started NameServer, waiting for connections.")
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt, shutting down ...")
        server.stop(1.0)
