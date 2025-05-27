all: services

services: src/common/protos/*.proto
	rm -rf src/common/rpc
	mkdir src/common/rpc/
	mkdir src/common/rpc/services
	mkdir src/common/rpc/types
	python -m grpc_tools.protoc -Isrc/common/protos --python_out=src/common/rpc/types --pyi_out=src/common/rpc/types --grpc_python_out=src/common/rpc/services $?