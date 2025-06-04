all: services

services: src/common/protos/*.proto
	rm -rf src/common/rpc
	mkdir src/common/rpc/

	python -m grpc_tools.protoc -Isrc/common/protos -Igoogleapis --python_out=src/common/rpc/ --pyi_out=src/common/rpc/ --grpc_python_out=src/common/rpc/ $?