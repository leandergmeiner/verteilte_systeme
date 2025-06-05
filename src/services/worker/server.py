import logging
from concurrent import futures

import grpc

from src.services.worker.service import WorkerServicer, worker_pb2_grpc
import os
logger = logging.getLogger()



def create_server(
    task_type: str,
    server_address: str, # Can't determine the address
    name_server_address: str | None = "localhost:50051",
):
    name_server_address = name_server_address or os.environ.get("NAME_SERVICE")

    if name_server_address is None:
        raise ValueError("Unknown name service address.")
    server = grpc.server(futures.ThreadPoolExecutor())
    worker_pb2_grpc.add_WorkerServicer_to_server(WorkerServicer(task_type, server_address, name_server_address), server)
    _port = server.add_insecure_port(server_address)
    try:
        server.start()
        logger.info("Started worker with type %s, waiting for connections.", task_type)
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt, shutting down ...")
        server.stop(1.)
