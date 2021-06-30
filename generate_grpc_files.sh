protoc --go_out='./go_backend' --go-grpc_out='./go_backend' ./grpc_utils/node_grpc.proto

python -m grpc_tools.protoc -I./ --python_out='./' --grpc_python_out='./' ./grpc_utils/node_grpc.proto
sed -i 's/import node_grpc_pb2 as node__grpc__pb2/from . import node_grpc_pb2 as node__grpc__pb2/' './grpc_utils/node_grpc_pb2_grpc.py'

python -m grpc_tools.protoc -I./ --python_out='./' --grpc_python_out='./' ./grpc_utils/kvstore.proto
sed -i 's/import kvstore_pb2 as kvstore__pb2/from . import kvstore_pb2 as kvstore__pb2/' './grpc_utils/kvstore_pb2_grpc.py'

echo "Genrated files in respective locations"