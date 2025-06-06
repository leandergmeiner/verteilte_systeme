import sys

sys.path.append("src/common/rpc")  # Needed because of protobuf


import logging

import fire

from src.services import client, dispatcher, nameserver, worker


def main():
    logging.basicConfig(level=logging.INFO)
    fire.Fire(
        {
            "dispatcher": dispatcher.create_server,
            "nameserver": nameserver.create_server,
            "worker": worker.create_server,
            "exec": client.execute_command,
            "help": client.worker_help,
        }
    )


if __name__ == "__main__":
    main()
