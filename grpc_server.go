package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"

	"github.com/kishansairam9/ShardedKVStore/node"
	"google.golang.org/grpc"
)

type nodeGrpcServer struct {
	node.NodeServer
	s *node.Store
}

func (r *nodeGrpcServer) Init(ctx context.Context, config *node.InitConfig) (*node.OneString, error) {
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

func (r *nodeGrpcServer) Join(ctx context.Context, config *node.JoinConfig) (*node.OneString, error) {
	var ret node.OneString
	if r.s == nil {
		ret.Msg = "ERR:Server not initialized, call init first"
		return &ret, nil
	}
	ret.Msg = r.s.Join(config.NodeID, config.Addr)
	return &ret, nil
}

func (r *nodeGrpcServer) Put(ctx context.Context, config *node.KVPair) (*node.OneString, error) {
	var ret node.OneString
	if r.s == nil {
		ret.Msg = "ERR:Server not initialized, call init first"
		return &ret, nil
	}
	ret.Msg = r.s.Put(config.Key, config.Val)
	return &ret, nil
}

func (r *nodeGrpcServer) Get(ctx context.Context, config *node.OneString) (*node.OneString, error) {
	var ret node.OneString
	if r.s == nil {
		ret.Msg = "ERR:Server not initialized, call init first"
		return &ret, nil
	}
	ret.Msg = r.s.Get(config.Msg)
	return &ret, nil
}

func (r *nodeGrpcServer) Delete(ctx context.Context, config *node.OneString) (*node.OneString, error) {
	var ret node.OneString
	if r.s == nil {
		ret.Msg = "ERR:Server not initialized, call init first"
		return &ret, nil
	}
	ret.Msg = r.s.Delete(config.Msg)
	return &ret, nil
}

func (r *nodeGrpcServer) Close(ctx context.Context, config *node.OneString) (*node.OneString, error) {
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

	r := nodeGrpcServer{}
	r.s = nil

	grpcServer := grpc.NewServer()

	node.RegisterNodeServer(grpcServer, &r)

	// Run GPRC Server concurrently and main waits for interrupts to exit gracefully
	go func() {
		if err := grpcServer.Serve(lis); err != nil {
			log.Fatalf("Failed to serve Grpc on port %v\n%v", string(os.Args[1]), err)
		}
	}()

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, os.Interrupt, syscall.SIGTERM)
	<-sigs
	fmt.Println("\nRecieved terminate signal, closing DB to exit gracefully")
	r.s.Close()
}
