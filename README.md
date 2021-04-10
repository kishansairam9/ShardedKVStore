# Sharded Key Value Store

## Architecture

- Replication implemented using Raft consensus algorithm (used hashicorp's go implementation)
- Interfaced "node" (each element in replica set) using GRPC from python
- Each "shard" is implemented as a set of nodes taking part in raft consensus
- "KVStore" is implemented as a set of shards.

## Data Storage

- Data storage can be done only in memory, but this doesn't scale, hence used Disk backed KV Store at each node
- Utilized [Bitcask](https://github.com/prologic/bitcask). Supports fast access to upto 1M KV Pairs using disk as backing store
- If we want to scale even further to billions of records for each node we should use LevelDB for reasons mentioned [here](https://github.com/prologic/bitcask#is-bitcask-right-for-my-project)
- Since we are already sharding based on key, we stick to using Bitcask as after sharding key space for each node is reduced
- Due to modular implementation, it allows for easy replacement of backing store, primarily `node/fsm.go` has to be modified

## Implementation Files and Directory Structure

```
.
├── Pipfile <Python Env>
├── Pipfile.lock <Python Env>
├── README.md
├── client.py <Wrapper Client> ||* GRPC Client Wrapper File *||
├── go.mod <Go Env>
├── go.sum <Go Env>
├── kvstore <Python implementation of Store>
│   ├── node.py <Node of replica set implemented using GRPC to Golang Node>
│   ├── shard.py <Shard as a replica set of nodes>
│   ├── store.py <Store as a collection of shards>
│   └── utils.py <Custom Exceptions>
├── kvstore.proto <Protobuf for KVStore service>
├── kvstore_grpc_server.py <KVStore GRPC Server> ||* File to run Server *||
├── node <Golang node implementation based on hashicorp raft>
│   ├── fsm.go <FSM for raft>
│   ├── node_grpc.pb.go <GRPC generated file>
│   ├── node_grpc_grpc.pb.go <GRPC generated file>
│   └── store.go <Node interface as a KVStore>
├── node_grpc.proto <Protobuf for Node in Golang>
├── node_grpc_server.go <Golang Node GRPC Server>
├── protoc_command.sh <Script for updating protobuf generated files>
└── python_grpc <GRPC Generated files>
    ├── kvstore_pb2.py
    ├── kvstore_pb2_grpc.py
    ├── node_grpc_pb2.py
    └── node_grpc_pb2_grpc.py
```

## Setup
- Install go lang from offical site
- Run `go mod tidy` inside main directory to fetch all required packages
- Install pipenv on your system and then run pipenv shell from repo root to activate virtual env
    - If pipenv complains about python version 3.9.2, ignore it and force python version using `--python` flag, any version >=3.7 should work
- Modify `ABS_REPO_ROOT` in `kvstore/node.py` to reflect the absolute location of the repo on your system

## KVStore Server
- Run `python3 kvstore_grpc_server.py <LOG_DIR_LOCATION>` to run GRPC Server for KVStore using default parameters
```
usage: kvstore_grpc_server.py [-h] [--port PORT] [--shard_cnt SHARD_CNT] [--replica_cnt REPLICA_CNT] [--max_workers MAX_WORKERS] storage_loc

KVStore Server Parameters

positional arguments:
  storage_loc           Location for storage of all logging and database

optional arguments:
  -h, --help            show this help message and exit
  --port PORT           Port of grpc server
  --shard_cnt SHARD_CNT
                        No of shards
  --replica_cnt REPLICA_CNT
                        No of replias for each shard
  --max_workers MAX_WORKERS
                        Max workers for grpc threadpool
```

## Client
- Clients interact using GRPC, a wrapper `client.py` is provided to handle GRPC requests to server
- Import `RequestWrapper` class from `client.py` and use it to perform interactions with KVStore by passing in location of GRPC Server
- Example run from python3 interpreter at root of repo
```
>>> from client import *
>>> t = RequestWrapper('localhost:7000')
>>> t.get('k1')
'v1'
>>> t.put('k3', 'v3')
>>> t.get('k3')
'v3'
>>> t.delete('k3')
>>> t.get('k3')
>>> t.get('k1')
'v1'
```

## References

- Following repos were refered while implementing replication based on raft consensus
    - https://github.com/otoolep/hraftd 
    - https://github.com/prologic/bitraft