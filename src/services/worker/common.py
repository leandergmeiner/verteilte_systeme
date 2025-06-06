import typing
from abc import ABC
from src.common.rpc import worker_pb2


class TaskDispatcher(ABC):
    def process_task(
        self, arguments: typing.Iterable[str]
    ) -> tuple[bool, typing.Iterable[str]]: ...
    def get_status(self) -> worker_pb2.WorkerStatus: ...
