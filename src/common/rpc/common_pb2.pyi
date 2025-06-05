from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Task(_message.Message):
    __slots__ = ("task_id", "payload")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    task_id: int
    payload: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_id: _Optional[int] = ..., payload: _Optional[_Iterable[str]] = ...) -> None: ...

class TaskResult(_message.Message):
    __slots__ = ("task_id", "payload", "valid")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    VALID_FIELD_NUMBER: _ClassVar[int]
    task_id: int
    payload: _containers.RepeatedScalarFieldContainer[str]
    valid: bool
    def __init__(self, task_id: _Optional[int] = ..., payload: _Optional[_Iterable[str]] = ..., valid: bool = ...) -> None: ...

class ServiceIPWithPort(_message.Message):
    __slots__ = ("ip", "port")
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    port: int
    def __init__(self, ip: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...

class ExecuteTaskRequest(_message.Message):
    __slots__ = ("type", "payload")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    type: str
    payload: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(self, type: _Optional[str] = ..., payload: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...) -> None: ...
