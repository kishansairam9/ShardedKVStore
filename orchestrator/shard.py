from .utils import *
from time import sleep
import random
from .node import Node
from typing import List
import socket
import grpc

def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def makesure_ports_valid(ports: List[int]):
    curr_max = max(ports)
    valid = list(map(is_port_free, ports))
    for i in range(len(ports)):
        if not valid[i]:
            curr = curr_max + 1
            while not is_port_free(curr):
                curr +=1
            ports[i] = curr
            curr_max = curr

class Shard:
    '''Implements Shard as a replica set of nodes'''
    
    def __init__(self, replica_count: int, log_dir_path: str, raft_dir_path: str, store_dir_path: str, base_grpc_port: int = None, base_raft_port: int = None, wait_time: int = 5):
        nodes: dict = {}
        if base_grpc_port is None:
            base_grpc_port = random.randint(20000, 30000-1) # Choose random base port from registered ports
        if base_raft_port is None:
            base_raft_port = random.randint(30000, 40000) # Choose random base port from registered ports
        grpc_ports = [base_grpc_port + i for i in range(replica_count)]
        raft_ports = [base_raft_port + i for i in range(replica_count)]
        makesure_ports_valid(grpc_ports)
        makesure_ports_valid(raft_ports)
        for i in range(replica_count):
            try:
                suffix = f"/node_{i}"
                nodes[i] = Node(grpc_port=grpc_ports[i], log_path=log_dir_path+suffix)
                print(nodes[i].init(raft_dir=raft_dir_path+suffix, raft_port=raft_ports[i], store_dir=store_dir_path+suffix, node_id=i), f"node_id {i}")
            except ReturnedError as e:
                # Delete all connections
                del nodes
                raise ReturnedError(f"Failed to setup node id {i} at grpc {grpc_ports[i]}, raftport {raft_ports[i]}, using suffix as {suffix} :\n{e}")
        self.nodes = nodes
        sleep(wait_time) # Need to wait for inital raft setup to place
        # Choose random leader initially
        self.leader_id = list(nodes.keys())[0]
        for id in nodes.keys():
            if id == self.leader_id:
                continue
            try:
                print(nodes[self.leader_id].join(id, nodes[id].raft_port))
            except ReturnedError as e:
                # Delete all connections
                del nodes
                raise ReturnedError(f"Failed to join node {id} at raft port {nodes[id].raft_port}:\n{e}")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    raise GrpcError(f"TIMEOUT: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Process suspended or Network Partition or Timeout of {self.nodes[id].timeout} Low")
                elif e.code() == grpc.StatusCode.UNAVAILABLE:
                    raise GrpcError(f"UNAVAILABE: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Grpc server not found")

    def update_leader(self):
        inactive_ones = []
        for id in self.nodes.keys():
            try:
                if self.nodes[id].is_leader():
                    self.leader_id = id
                    return
            except ReturnedError as e:
                raise ReturnedError(f"Failed to check if node {id} at raft port {self.nodes[id].raft_port} is leader:\n{e}")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    print(f"TIMEOUT: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Process suspended or Network Partition or Timeout of {self.nodes[id].timeout} Low")
                elif e.code() == grpc.StatusCode.UNAVAILABLE:
                    print(f"UNAVAILABE: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Grpc server not found")
                inactive_ones.append(id)
        # No one is leader, has more failures than raft can handle!
        # Force kill and respawn all failed processes
        print("Has more failures than raft can handle!!!")
        print("Force killing all inactive ones and respawning")
        for id in inactive_ones:
            self.nodes[id].force_kill_and_respawn()
    
    def get(self, key: str, already_tried: set = set()):
        # Try to choose randomly to one of nodes
        to_try = set(self.nodes.keys()) - already_tried
        if len(to_try) == 0:
            raise GrpcError("Wasn't able to reach any node through Grpc, check server side printed log to know all nodes offline")
        id = random.choice(list(to_try))
        try:
            return self.nodes[id].get(key)
        except ReturnedError as e:
            # Get only fails when there is no key present typically
            print(f"Failed to get on node {id} at raft port {self.nodes[id].raft_port}:\n{e}")
            return None
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                print(f"TIMEOUT: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Process suspended or Network Partition or Timeout of {self.nodes[id].timeout} Low")
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                print(f"UNAVAILABE: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Grpc server not found")
            already_tried.add(id)
            self.get(key, already_tried)

    def put(self, key: str, val: str):
        id = self.leader_id
        try:
            self.nodes[id].put(key, val)
        except StaleLeader:
            self.update_leader()
            self.put(key, val)
        except ReturnedError as e:
            raise ReturnedError(f"Failed to put on leader node {id} at raft port {self.nodes[id].raft_port}:\n{e}")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                print(f"TIMEOUT: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Process suspended or Network Partition or Timeout of {self.nodes[id].timeout} Low")
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                print(f"UNAVAILABE: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Grpc server not found")
            self.update_leader()
            self.put(key, val)
    
    def delete(self, key: str):
        id = self.leader_id
        try:
            self.nodes[id].delete(key)
        except StaleLeader:
            self.update_leader()
            self.delete(key)
        except ReturnedError as e:
            raise ReturnedError(f"Failed to put on leader node {id} at raft port {self.nodes[id].raft_port}:\n{e}")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                print(f"TIMEOUT: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Process suspended or Network Partition or Timeout of {self.nodes[id].timeout} Low")
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                print(f"UNAVAILABE: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Grpc server not found")
            self.update_leader()
            self.delete(key)



