import sys

sys.path.append("src/common/rpc")  # Needed because of protobuf


import logging
import fire


from src.services import dispatcher, nameserver, worker


def main():
    logging.basicConfig(level=logging.INFO)
    fire.Fire(
        {
            "dispatcher": dispatcher.create_server,
            "nameserver": nameserver.create_server,
            "worker": worker.create_server,
        }
    )


if __name__ == "__main__":
    main()
