import logging
import os
import sys
from concurrent import futures
from pathlib import Path

import grpc

from src.services.worker.service import WorkerServicer, worker_pb2_grpc

logger = logging.getLogger()


def create_server(
    task_type: str,
    server_address: str,  # Can't determine the address
    name_server_address: str | None = "0.0.0.0:50051",
    registered_server_address: str = "",  # Server address given to the nameserver during registration
    log_dir: str = None,
):
    log_dir = log_dir or "logs"
    log_file = Path(log_dir, f"{task_type}-worker.txt")
    # Delete old logs
    if os.path.exists(log_file):
        os.remove(log_file)

    logging.basicConfig(level=logging.INFO, filename=log_file, filemode="a")
    logger.addHandler(logging.StreamHandler(sys.stdout))

    # if the server address to register to the name server does not differ it should be equal to the server address
    if not registered_server_address:
        registered_server_address = server_address

    name_server_address = name_server_address or os.environ.get("NAME_SERVICE")
    if name_server_address is None:
        raise ValueError("Unknown name service address.")
    server = grpc.server(futures.ThreadPoolExecutor())
    worker_pb2_grpc.add_WorkerServicer_to_server(
        WorkerServicer(task_type, registered_server_address, name_server_address),
        server,
    )
    _port = server.add_insecure_port(server_address)
    try:
        server.start()
        logger.info("Started worker with type %s, waiting for connections.", task_type)
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt, shutting down ...")
        server.stop(1.0)
