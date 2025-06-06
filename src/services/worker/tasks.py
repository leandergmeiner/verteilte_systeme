import typing

from src.common.rpc import worker_pb2
from src.services.worker.common import TaskDispatcher


class HashTaskDispatcher(TaskDispatcher):
    def __init__(self, hash_fn):
        self.hash_fn = hash_fn

    def process_task(
        self, arguments: typing.Iterable[str]
    ) -> tuple[bool, typing.Iterable[str]]:
        return True, (self.hash_fn(arg) for arg in arguments)

    def get_status(self):
        return worker_pb2.WorkerStatus(
            usage="""Expected arguments: list of strings
Returns: hashed integer values of the strings
""",
        )


class ReverseTaskDispatcher(TaskDispatcher):
    def process_task(
        self, arguments: typing.Iterable[str]
    ) -> tuple[bool, typing.Iterable[str]]:
        return True, (arg[::-1] for arg in arguments)

    def get_status(self):
        return worker_pb2.WorkerStatus(
            usage="""Expected arguments: list of strings
Returns: Reversed strings
""",
        )


class SumTaskDispatcher(TaskDispatcher):
    def process_task(
        self, arguments: typing.Iterable[str]
    ) -> tuple[bool, typing.Iterable[str]]:
        try:
            return True, (str(sum(int(arg) for arg in arguments)),)
        except ValueError:
            return False, ""

    def get_status(self):
        return worker_pb2.WorkerStatus(
            usage="""Expected arguments: list integers
Returns: The sum of the integers
""",
        )
