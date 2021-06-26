from kvstore.internal_node import InternalNode as Node

import os
import socket
import argparse
import Pyro5.server
import Pyro5.nameserver
import random

Pyro5.config.COMMTIMEOUT = 3
Pyro5.config.MAX_RETRIES = 1

KEEP_ON = True

def status():
    return KEEP_ON

def is_port_not_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

@Pyro5.server.behavior(instance_mode="single")
class DistributedMachine:

    def __init__(self) -> None:
        self.nodes = []
        self.curr_max_port = random.randint(30000, 40000)

    def get_port(self):
        port = self.curr_max_port+1
        while is_port_not_free(port):
            port += 1
        self.curr_max_port = port
        return port

    @Pyro5.server.expose
    def store_meta(self, ip, port):
        self.ip = ip
        self.port = port

    @Pyro5.server.expose
    def num_nodes(self):
        return len(self.nodes)

    @Pyro5.server.expose  
    def add_node(self, *args, **kwargs):
        if 'log_path' in kwargs:
            if kwargs['log_path'][0] != '/':
                kwargs['log_path'] = f"{os.getenv('PWD')}/" + kwargs['log_path']
            os.system(f"mkdir -p {kwargs['log_path']}")
        self.nodes.append(Node(*args, grpc_port=self.get_port(), **kwargs))
        return len(self.nodes) - 1

    @Pyro5.server.expose
    def init(self, idx, *args, **kwargs):
        assert idx < len(self.nodes), "Invalid Node ID"
        if 'raft_dir' in kwargs:
            if kwargs['raft_dir'][0] != '/':
                kwargs['raft_dir'] = f"{os.getenv('PWD')}/" + kwargs['raft_dir']
            os.system(f"mkdir -p {kwargs['raft_dir']}")
        if 'store_dir' in kwargs:
            if kwargs['store_dir'][0] != '/':
                kwargs['store_dir'] = f"{os.getenv('PWD')}/" + kwargs['store_dir']
            os.system(f"mkdir -p {kwargs['store_dir']}")
        ret_dict = self.nodes[idx].init(*args, raft_port=self.get_port(), **kwargs)
        ret_dict['ip'] = self.ip
        return ret_dict

    @Pyro5.server.expose
    def is_leader(self, idx):
        assert idx < len(self.nodes), "Invalid Node ID"
        return self.nodes[idx].is_leader()
    
    @Pyro5.server.expose
    def join(self, idx, *args, **kwargs):
        assert idx < len(self.nodes), "Invalid Node ID"
        return self.nodes[idx].join(*args, **kwargs)

    @Pyro5.server.expose
    def get(self, idx, *args, **kwargs):
        assert idx < len(self.nodes), "Invalid Node ID"
        return self.nodes[idx].get(*args, **kwargs)
    
    @Pyro5.server.expose
    def put(self, idx, *args, **kwargs):
        assert idx < len(self.nodes), "Invalid Node ID"
        return self.nodes[idx].put(*args, **kwargs)

    @Pyro5.server.expose
    def delete(self, idx, *args, **kwargs):
        assert idx < len(self.nodes), "Invalid Node ID"
        return self.nodes[idx].delete(*args, **kwargs)

    @Pyro5.server.expose
    def close(self, idx, *args, **kwargs):
        assert idx < len(self.nodes), "Invalid Node ID"
        return self.nodes[idx].close(*args, **kwargs)

    @Pyro5.server.expose
    def force_kill(self, idx, *args, **kwargs):
        assert idx < len(self.nodes), "Invalid Node ID"
        return self.nodes[idx].force_kill(*args, **kwargs)

    @Pyro5.server.expose
    def force_init(self, idx, *args, **kwargs):
        assert idx < len(self.nodes), "Invalid Node ID"
        return self.nodes[idx].force_init(*args, **kwargs)

    @Pyro5.server.expose
    def clear_node(self, idx):
        self.nodes[idx] = None

    @Pyro5.server.expose
    def shutdown(self):
        global KEEP_ON
        KEEP_ON = False

    def __del__(self):
        del self.nodes

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='KVStore Server Parameters')
    parser.add_argument('--port', type=int, default=7940, help='Port of rmi server')
    args = parser.parse_args()

    def custom_error_handler(daemon, client_sock, method, vargs, kwargs, exception):
        print("\nERROR IN METHOD CALL USER CODE:")
        print(" client={} method={} exception={}".format(client_sock, method.__qualname__, repr(exception)))

    DEBUG = False # True sets custom_error_handler for DEBUGGING 

    with Pyro5.server.Daemon(host='0.0.0.0', port=args.port) as deamon:
        deamon.methodcall_error_handler = custom_error_handler if DEBUG else None 
        uri = deamon.register(DistributedMachine, objectId='kvstore-machinermi')
        print(f"Distributed Machine Server started at {uri}")
        deamon.requestLoop(status)
    