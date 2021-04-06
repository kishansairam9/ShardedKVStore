from socket import timeout
import sys
sys.path.append('..')
import subprocess
import grpc
from python_grpc import node_grpc_pb2_grpc
from python_grpc import node_grpc_pb2
from .utils import *
from time import sleep

GO_SERVER_PATH = '/Users/kishanadapa9/Repositories/ShardedKVStore/grpc_server.go'

def decode_response(resp: str):
    # Shouldn't call strip here on any string
    # As it can remove trailing or start spaces in get
    col = resp.index(':')
    status = resp[:col]
    msg = resp[col+1:]
    return status, msg

class Node:
    '''Implements node interface with GRPC'''

    def __init__(self, grpc_port: int, log_path: str, timeout: int = 2):
        self.timeout = timeout
        self.grpc_port = grpc_port
        self.log_path = log_path
        self.log_file = open(log_path, 'w')
        self.process = subprocess.Popen(f"go run {GO_SERVER_PATH} {grpc_port}", shell=True, stdout=self.log_file, stderr=self.log_file)
        self.channel = grpc.insecure_channel(f'localhost:{grpc_port}')
        self.stub = node_grpc_pb2_grpc.NodeStub(self.channel)

    def init(self, raft_dir: str, raft_port: int, store_dir: str, node_id: int):
        self.raft_dir = raft_dir
        self.raft_port = raft_port
        self.store_dir = store_dir
        self.node_id = node_id
        request = node_grpc_pb2.InitConfig(RaftDir=raft_dir, RaftAddr=f'localhost:{raft_port}', StoreDir=store_dir, NodeID=str(node_id))
        resp = self.stub.Init(request, timeout=self.timeout)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        return msg

    def is_leader(self):
        request = node_grpc_pb2.OneString(Msg='blah') # Message will be ignored
        resp = self.stub.Close(request, timeout=self.timeout)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        return not (status == 'NONLEADER')
    
    def join(self, node_id: str, raft_port: int):
        request = node_grpc_pb2.JoinConfig(NodeID=str(node_id), Addr=f'localhost:{raft_port}')
        resp = self.stub.Join(request, timeout=self.timeout)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        return msg

    def get(self, key: str):
        request = node_grpc_pb2.OneString(Msg=key)
        resp = self.stub.Get(request, timeout=self.timeout)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        return msg
    
    def put(self, key: str, value: str):
        request = node_grpc_pb2.KVPair(Key=key, Val=value)
        resp = self.stub.Put(request, timeout=self.timeout)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        if status == 'NONLEADER':
            raise StaleLeader()
        return msg

    def delete(self, key: str):
        request = node_grpc_pb2.OneString(Msg=key)
        resp = self.stub.Delete(request, timeout=self.timeout)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        return msg

    def close(self):
        request = node_grpc_pb2.OneString(Msg='blah') # Message will be ignored
        resp = self.stub.Close(request, timeout=self.timeout)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        return msg

    def force_kill_and_respawn(self):
        print(f"Called force kill and respawn kill an node id {self.node_id}")
        self.process.kill()
        self.__init__(self.grpc_port, self.log_path, self.timeout)
        self.init(self.raft_dir, self.raft_port, self.store_dir, self.node_id)
        print(f"Succesfully killed and respawned node {self.node_id}")

    def __del__(self):
        self.process.terminate()
        self.log_file.close()