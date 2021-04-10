from .utils import *
from .shard import Shard

import hashlib

class Store:
    """Implements Store as a set of shards being hashed into"""

    def __init__(self, shard_cnt: int, replica_cnt: int, storage_loc: str, base_raft_port: int = 37689):
        self.log_dir = storage_loc + '/logs'
        self.raft_dir = storage_loc + '/raft'
        self.store_dir = storage_loc + '/store'
        self.shard_cnt = shard_cnt
        self.shards = []
        for i in range(shard_cnt):
            suffix = f'/shard{i}'
            self.shards.append(Shard(replica_cnt, self.log_dir+suffix, self.raft_dir+suffix, self.store_dir+suffix, base_raft_port+i*replica_cnt, print_name=f'SHARD {i}'))

    def hash_key(self, s):
        return int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16) % (self.shard_cnt)

    def put(self, key, val):
        try:
            return (True, self.shards[self.hash_key(key)].put(key, val))
        except Exception as e:
            return (False, f"ERROR: {e}")

    def get(self, key):
        try:
            return (True, self.shards[self.hash_key(key)].get(key))
        except Exception as e:
            return (False, f"ERROR: {e}")

    def delete(self, key):
        try:
            return (True, self.shards[self.hash_key(key)].delete(key))
        except Exception as e:
            return (False, f"ERROR: {e}")
        

