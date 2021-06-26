from .utils import *
from .machines import machines, locks

def decode_response(resp):
    # Shouldn't call strip here on any string
    # As it can remove trailing or start spaces in get
    col = resp.index(':')
    status = resp[:col]
    msg = resp[col+1:]
    return status, msg

class Node:

    def __init__(self, machine_idx, *args, **kwargs) -> None:
        # NOTE: Can add better scheduling based on num of nodes currently on each machine
        self.machine_idx = machine_idx
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            self.idx = machines[self.machine_idx].add_node(*args, **kwargs)

    def init(self, *args, **kwargs):
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            ret_dict = machines[self.machine_idx].init(self.idx, *args, **kwargs)
        self.raft_dir = f"{ret_dict['ip']}:" + str(ret_dict['raft_dir'])
        self.store_dir = f"{ret_dict['ip']}:" + str(ret_dict['store_dir'])
        self.raft_port = f"{ret_dict['ip']}:" + str(ret_dict['raft_port'])
        self.node_id = ret_dict['node_id']
        self.timeout = ret_dict['timeout']
        self.grpc_port = f"{ret_dict['ip']}:" + str(ret_dict['grpc_port'])
        self.log_path = f"{ret_dict['ip']}:" + str(ret_dict['log_path'])
        status, msg = decode_response(ret_dict['resp'])
        if status == 'ERR':
            raise ReturnedError(msg)
        return msg

    def is_leader(self):
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            resp = machines[self.machine_idx].is_leader(self.idx)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        return not (status == 'NONLEADER')
    
    def join(self, *args, **kwargs):
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            resp = machines[self.machine_idx].join(self.idx, *args, **kwargs)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        return msg

    def get(self, *args, **kwargs):
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            resp = machines[self.machine_idx].get(self.idx, *args, **kwargs)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        return msg
    
    def put(self, *args, **kwargs):
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            resp = machines[self.machine_idx].put(self.idx, *args, **kwargs)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        if status == 'NONLEADER':
            raise StaleLeader()
        return msg

    def delete(self, *args, **kwargs):
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            resp = machines[self.machine_idx].delete(self.idx, *args, **kwargs)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        if status == 'NONLEADER':
            raise StaleLeader()
        return msg

    def close(self, *args, **kwargs):
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            resp = machines[self.machine_idx].close(self.idx, *args, **kwargs)
        status, msg = decode_response(resp)
        if status == 'ERR':
            raise ReturnedError(msg)
        return msg
        
    def force_kill(self, print_fn):
        print_fn(f"Called force kill and respawn an node id {self.node_id}", 'yellow')
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            return machines[self.machine_idx].force_kill(self.idx)

    def force_init(self, print_fn = print):
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            machines[self.machine_idx].force_init(self.idx)
        print_fn(f"Succesfully killed and respawned node {self.node_id}", 'green')

    def __del__(self):
        with locks[self.machine_idx]:
            machines[self.machine_idx]._pyroClaimOwnership()
            machines[self.machine_idx].clear_node(self.idx)
