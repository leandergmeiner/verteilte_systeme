# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: common.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'common.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x63ommon.proto\x12\x08services\"(\n\x04Task\x12\x0f\n\x07task_id\x18\x01 \x01(\r\x12\x0f\n\x07payload\x18\x03 \x03(\t\"=\n\nTaskResult\x12\x0f\n\x07task_id\x18\x01 \x01(\r\x12\x0f\n\x07payload\x18\x02 \x03(\t\x12\r\n\x05valid\x18\x03 \x01(\x08\"-\n\x11ServiceIPWithPort\x12\n\n\x02ip\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\r\"3\n\x12\x45xecuteTaskRequest\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0f\n\x07payload\x18\x02 \x03(\tb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'common_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_TASK']._serialized_start=26
  _globals['_TASK']._serialized_end=66
  _globals['_TASKRESULT']._serialized_start=68
  _globals['_TASKRESULT']._serialized_end=129
  _globals['_SERVICEIPWITHPORT']._serialized_start=131
  _globals['_SERVICEIPWITHPORT']._serialized_end=176
  _globals['_EXECUTETASKREQUEST']._serialized_start=178
  _globals['_EXECUTETASKREQUEST']._serialized_end=229
# @@protoc_insertion_point(module_scope)
