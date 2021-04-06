protoc --go_out='./' --go-grpc_out='./' ./node_grpc.proto
python -m grpc_tools.protoc -I./ --python_out='./python_grpc' --grpc_python_out='./python_grpc' ./node_grpc.proto
sed -i 's/import node_grpc_pb2 as node__grpc__pb2/from . import node_grpc_pb2 as node__grpc__pb2/' './python_grpc/node_grpc_pb2_grpc.py'