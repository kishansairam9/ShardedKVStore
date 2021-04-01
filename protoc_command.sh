protoc --go_out='./' --go-grpc_out='./' ./replica_set.proto
python -m grpc_tools.protoc -I./ --python_out='./client' --grpc_python_out='./client' ./replica_set.proto
