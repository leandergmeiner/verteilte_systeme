from googleapis.google.rpc import status_pb2 as _status_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Service(_message.Message):
    __slots__ = ("type", "ip")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    type: str
    ip: str
    def __init__(self, type: _Optional[str] = ..., ip: _Optional[str] = ...) -> None: ...
