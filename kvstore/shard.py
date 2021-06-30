from .utils import *
from .node import Node
from .machines import machines_meta

from time import sleep
from termcolor import cprint
import random
import grpc


class Shard:
    '''Implements Shard as a replica set of nodes'''

    def print(self, content: str, *args):
        pre = '' if self.print_name is None else self.print_name
        pre += ': '
        cprint(pre, 'blue', end='')
        cprint(content, *args)
    
    def __init__(self, replica_count: int, log_dir_path: str, raft_dir_path: str, store_dir_path: str, wait_time: int = 10, print_name: str = None):
        self.print_name = print_name
        nodes: dict = {}
        # NOTE: Recovery from previous logs is not possible in distributed version, check CAVEATS section of README
        self.log_dir_path = log_dir_path
        self.wait_time = wait_time
        # Choose any initial leader
        self.leader_id = random.randint(0, replica_count-1)
        for i in range(replica_count):
            midx = random.randint(0, len(machines_meta)-1)
            try:
                suffix = f"/node_{i}"
                nodes[i] = Node(machine_idx=midx,log_path=log_dir_path+suffix)
                while True:
                    # Wait for process to start
                    try:
                        self.print(f"{nodes[i].init(raft_dir=raft_dir_path+suffix,  store_dir=store_dir_path+suffix, node_id=i, leader=(i == self.leader_id))} at node_id {i}", 'green')
                        break
                    except Exception as e:
                        # print(e)
                        pass
            except ReturnedError as e:
                # Delete all connections
                del nodes
                raise ReturnedError(f"Failed to setup node id {i} on machine {machines_meta[i]}")
        self.nodes = nodes
        self.print(f"Waiting for {wait_time}s to let initial raft set up take place", 'yellow')
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
        self.print("Has more failures than raft can handle", 'red')
        self.print("Recovering by force killing all inactive ones and respawning", 'green')
        for id in inactive_ones:
            self.nodes[id].force_kill(self.print)
        sleep(self.wait_time)
        for id in inactive_ones:
            self.nodes[id].force_init(self.print)
        sleep(self.wait_time)
        self.update_leader()
    
    def get(self, key: str, already_tried = None):
        # Try to choose randomly to one of nodes
        already_tried = set() if already_tried is None else already_tried
        to_try = set(self.nodes.keys()) - already_tried
        if len(to_try) == 0:
            self.print("ERROR: Wasn't able to reach any node through Grpc", 'red')
            self.update_leader()
            return self.get(key, set())
        id = random.choice(list(to_try))
        try:
            return self.nodes[id].get(key)
        except ReturnedError as e:
            # Get only fails when there is no key present 
            # self.print(f"Returning none as failed to get on node {id} at raft port {self.nodes[id].raft_port}: {e}", 'green')
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

