cd go_backend
go mod tidy
go build node_grpc_server.go
# Remove existing installation
rm -rf ~/.local/bin/node_grpc_server
# Symlink
ln -s $PWD/node_grpc_server ~/.local/bin/node_grpc_server
echo "Built binary and symlinked to local bin successfully"
ls -l ~/.local/bin/node_grpc_server