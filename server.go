package main

import (
	"context"
	"fmt"
	"log"
	"net"

	"github.com/kishansairam9/ShardedKVStore/node"
	"google.golang.org/grpc"
)

type replicaSetServer struct {
	node.ReplicaSetServer
	s *node.Store
}

func (r *replicaSetServer) Init(ctx context.Context, config *node.InitConfig) (*node.OneString, error) {
	r.s = node.New(config.StoreDir)
	r.s.RaftDir = config.RaftDir
	r.s.RaftBind = config.RaftAddr
	var ret node.OneString
	ret.Msg = r.s.Open(config.Leader, config.NodeID)
	return &ret, nil
}

func (r *replicaSetServer) Join(ctx context.Context, config *node.JoinConfig) (*node.OneString, error) {
	var ret node.OneString
	ret.Msg = r.s.Join(config.NodeID, config.Addr)
	return &ret, nil
}

func (r *replicaSetServer) Put(ctx context.Context, config *node.KVPair) (*node.OneString, error) {
	var ret node.OneString
	fmt.Print(r.s)
	ret.Msg = r.s.Put(config.Key, config.Val)
	return &ret, nil
}

func (r *replicaSetServer) RemoveNode(ctx context.Context, config *node.OneString) (*node.OneString, error) {
	var ret node.OneString
	ret.Msg = r.s.RemoveNode(config.Msg)
	return &ret, nil
}

func (r *replicaSetServer) Get(ctx context.Context, config *node.OneString) (*node.OneString, error) {
	var ret node.OneString
	ret.Msg = r.s.Get(config.Msg)
	return &ret, nil
}

func (r *replicaSetServer) Delete(ctx context.Context, config *node.OneString) (*node.OneString, error) {
	var ret node.OneString
	ret.Msg = r.s.Delete(config.Msg)
	return &ret, nil
}

func main() {
	lis, err := net.Listen("tcp", ":9000")
	if err != nil {
		log.Fatalf("Failed to listen on port :9000 %v", err)
	}

	r := replicaSetServer{}

	grpcServer := grpc.NewServer()

	node.RegisterReplicaSetServer(grpcServer, &r)

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve Grpc on port :9000 %v", err)
	}
}
