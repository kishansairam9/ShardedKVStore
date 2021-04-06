protoc --go_out='./' --go-grpc_out='./' ./replica_set.proto
python -m grpc_tools.protoc -I./ --python_out='./python_grpc' --grpc_python_out='./python_grpc' ./replica_set.proto
sed -i 's/import replica_set_pb2 as replica__set__pb2/from .import replica_set_pb2 as replica__set__pb2/g' './python_grpc/replica_set_pb2_grpc.py'