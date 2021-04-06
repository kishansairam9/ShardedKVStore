package main

import (
	"context"
	"log"
	"net"
	"os"

	"github.com/kishansairam9/ShardedKVStore/node"
	"google.golang.org/grpc"
)

type replicaSetServer struct {
	node.ReplicaSetServer
	s *node.Store
}

func (r *replicaSetServer) Init(ctx context.Context, config *node.InitConfig) (*node.OneString, error) {
	var ret node.OneString
	r.s, ret.Msg = node.New(config.StoreDir)
	if r.s == nil {
		return &ret, nil
	}
	r.s.RaftDir = config.RaftDir
	r.s.RaftBind = config.RaftAddr
	ret.Msg = r.s.Open(config.Leader, config.NodeID)
	if ret.Msg[0] == 'E' {
		r.s = nil
	}
	return &ret, nil
}

func (r *replicaSetServer) Join(ctx context.Context, config *node.JoinConfig) (*node.OneString, error) {
	var ret node.OneString
	if r.s == nil {
		ret.Msg = "ERR:Server not initialized, call init first"
		return &ret, nil
	}
	ret.Msg = r.s.Join(config.NodeID, config.Addr)
	return &ret, nil
}

func (r *replicaSetServer) Put(ctx context.Context, config *node.KVPair) (*node.OneString, error) {
	var ret node.OneString
	if r.s == nil {
		ret.Msg = "ERR:Server not initialized, call init first"
		return &ret, nil
	}
	ret.Msg = r.s.Put(config.Key, config.Val)
	return &ret, nil
}

func (r *replicaSetServer) Get(ctx context.Context, config *node.OneString) (*node.OneString, error) {
	var ret node.OneString
	if r.s == nil {
		ret.Msg = "ERR:Server not initialized, call init first"
		return &ret, nil
	}
	ret.Msg = r.s.Get(config.Msg)
	return &ret, nil
}

func (r *replicaSetServer) Delete(ctx context.Context, config *node.OneString) (*node.OneString, error) {
	var ret node.OneString
	if r.s == nil {
		ret.Msg = "ERR:Server not initialized, call init first"
		return &ret, nil
	}
	ret.Msg = r.s.Delete(config.Msg)
	return &ret, nil
}

func (r *replicaSetServer) Close(ctx context.Context, config *node.OneString) (*node.OneString, error) {
	var ret node.OneString
	if r.s == nil {
		ret.Msg = "ERR:Server not initialized, call init first"
		return &ret, nil
	}
	ret.Msg = r.s.Close()
	return &ret, nil
}

func main() {
	lis, err := net.Listen("tcp", ":"+string(os.Args[1]))
	if err != nil {
		log.Fatalf("Failed to listen on port :9000 %v", err)
	}

	r := replicaSetServer{}
	r.s = nil

	grpcServer := grpc.NewServer()

	node.RegisterReplicaSetServer(grpcServer, &r)

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve Grpc on port %v\n%v", string(os.Args[1]), err)
	}
	r.s.Close()

}
