from .utils import *
from .node import Node

from time import sleep
from termcolor import cprint
import os
import random
from typing import List
import socket
import grpc

def is_port_not_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def makesure_ports_valid(ports: List[int]):
    curr_max = max(ports)
    not_valid = list(map(is_port_not_free, ports))
    for i in range(len(ports)):
        if not_valid[i]:
            curr = curr_max + 1
            while is_port_not_free(curr):
                curr +=1
            ports[i] = curr
            curr_max = curr

test_some = { # Used for purpose of manual testing
    'replica_count': 5,
    'log_dir_path': 'test/log',
    'raft_dir_path': 'test/raft',
    'store_dir_path': 'test/store',
    'print_name': 'TEST SHARD'
}

class Shard:
    '''Implements Shard as a replica set of nodes'''

    def print(self, content: str, *args):
        pre = '' if self.print_name is None else self.print_name
        pre += ': '
        cprint(pre, 'blue', end='')
        cprint(content, *args)
    
    def __init__(self, replica_count: int, log_dir_path: str, raft_dir_path: str, store_dir_path: str, base_raft_port: int = 34568, base_grpc_port: int = None, wait_time: int = 5, print_name: str = None):
        # Make sure they are valid paths
        os.system(f"mkdir -p {log_dir_path} {store_dir_path} {raft_dir_path}")
        self.print_name = print_name
        nodes: dict = {}
        # NOTE: For recovery to be possible previous set of raft ports must be same as current set of ports
        # TODO: Add a note that if base raft ports are random recovery from previous raft logs is not possible
        if base_grpc_port is None:
            base_grpc_port = random.randint(20000, 30000-1) # Choose random base port from registered ports
        if base_raft_port is None:
            base_raft_port = random.randint(30000, 40000) # Choose random base port from registered ports
        grpc_ports = [base_grpc_port + i for i in range(replica_count)]
        raft_ports = [base_raft_port + i for i in range(replica_count)]
        makesure_ports_valid(grpc_ports)
        for i in raft_ports:
            if is_port_not_free(i):
                raise ValueError(f"Raft port {i} not free, can't proceed forward make sure raft ports are free if passed base_raft_port as None, or else try invoking again with different base raft port")
        self.log_dir_path = log_dir_path
        self.wait_time = wait_time
        found_last_log = False
        try:
            # If last leader in log
            with open(f"{log_dir_path}/last_leader.log", 'r') as f:
                self.leader_id = int(f.readline().strip())
                if self.leader_id not in range(replica_count):
                    raise ValueError("Leader id from log greater not in range of ids for given replica count")
                found_last_log = True
        except:
            # Choose random leader initially
            self.leader_id = 0
        for i in range(replica_count):
            try:
                suffix = f"/node_{i}"
                nodes[i] = Node(grpc_port=grpc_ports[i], log_path=log_dir_path+suffix)
                while True:
                    # Wait for process to start
                    try:
                        self.print(f"{nodes[i].init(raft_dir=raft_dir_path+suffix, raft_port=raft_ports[i], store_dir=store_dir_path+suffix, node_id=i, leader=(i == self.leader_id))} at node_id {i}", 'green')
                        break
                    except:
                        pass
            except ReturnedError as e:
                # Delete all connections
                del nodes
                raise ReturnedError(f"Failed to setup node id {i} at grpc {grpc_ports[i]}, raftport {raft_ports[i]}, using suffix as {suffix} :\n{e}")
        self.nodes = nodes
        sleep(wait_time) # Need to wait for inital raft setup to place
        self.update_leader(True)
        self.print(f"Joining nodes to leader node {self.leader_id}", 'yellow')
        for id in nodes.keys():
            if id == self.leader_id:
                continue
            try:
                self.print(nodes[self.leader_id].join(id, nodes[id].raft_port), 'green')
            except ReturnedError as e:
                f_raft_port = nodes[id].raft_port
                # Delete all connections
                del nodes
                raise ReturnedError(f"Failed to join node {id} at raft port {f_raft_port}:\n{e}")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    raise GrpcError(f"TIMEOUT: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Process suspended or Network Partition or Timeout of {self.nodes[id].timeout} Low")
                elif e.code() == grpc.StatusCode.UNAVAILABLE:
                    raise GrpcError(f"UNAVAILABE: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Grpc server not found")
        sleep(wait_time)
        self.update_leader()

    def update_leader(self, dont_check_failures: bool = False):
        inactive_ones = []
        for id in self.nodes.keys():
            try:
                if self.nodes[id].is_leader():
                    self.leader_id = id
                    with open(f"{self.log_dir_path}/last_leader.log", 'w') as f:
                        print(self.leader_id, file=f)
                    return
            except ReturnedError as e:
                raise ReturnedError(f"Failed to check if node {id} at raft port {self.nodes[id].raft_port} is leader:\n{e}")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    self.print(f"TIMEOUT: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Process suspended or Network Partition or Timeout of {self.nodes[id].timeout} Low", 'yellow')
                elif e.code() == grpc.StatusCode.UNAVAILABLE:
                    self.print(f"UNAVAILABE: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Grpc server not found", 'yellow')
                inactive_ones.append(id)
        if dont_check_failures:
            self.print("WARN: Reached more failures than can handle but don't check more failures was passed!", 'yellow')
            return
        # No one is leader, has more failures than raft can handle!
        # Force kill and respawn all failed processes
        self.print("Has more failures than raft can handle for write / deletes", 'red')
        self.print("Force killing all inactive ones and respawning", 'green')
        for id in inactive_ones:
            self.nodes[id].force_kill(self.print)
        sleep(self.wait_time)
        for id in inactive_ones:
            self.nodes[id].force_init(self.print)
        sleep(self.wait_time)
        self.update_leader()
    
    def get(self, key: str, already_tried: set = set()):
        # Try to choose randomly to one of nodes
        to_try = set(self.nodes.keys()) - already_tried
        if len(to_try) == 0:
            self.print("ERROR: Wasn't able to reach any node through Grpc, check server side printed log to know all nodes offline", 'red')
            return -1
        id = random.choice(list(to_try))
        try:
            return self.nodes[id].get(key)
        except ReturnedError as e:
            # Get only fails when there is no key present typically
            self.print(f"Returning none as failed to get on node {id} at raft port {self.nodes[id].raft_port}: {e}", 'green')
            return None
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                self.print(f"TIMEOUT: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Process suspended or Network Partition or Timeout of {self.nodes[id].timeout} Low", 'yellow')
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                self.print(f"UNAVAILABE: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Grpc server not found", 'yellow')
            already_tried.add(id)
            return self.get(key, already_tried)

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
                self.print(f"TIMEOUT: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Process suspended or Network Partition or Timeout of {self.nodes[id].timeout} Low", 'yellow')
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                self.print(f"UNAVAILABE: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Grpc server not found", 'yellow')
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
                self.print(f"TIMEOUT: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Process suspended or Network Partition or Timeout of {self.nodes[id].timeout} Low", 'yellow')
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                self.print(f"UNAVAILABE: Node {id} at raft port {self.nodes[id].raft_port}, grpc port {self.nodes[id].grpc_port} - Grpc server not found", 'yellow')
            self.update_leader()
            self.delete(key)

