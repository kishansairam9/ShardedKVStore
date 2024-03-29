# Sharded Key / Value Store <!-- omit in toc -->

Demo Video - [Onedrive Link](https://iiitaphyd-my.sharepoint.com/:v:/g/personal/kishan_sairam_students_iiit_ac_in/EYLDYB0E8UlNvmKRPVjKjO4BDXan5A2L_ENU8czE9Bs7VA) 
* Enable 720p, lower resolutions look blurry with text
* Kindly note the results in video are poor due to being run on a dual core Macbook Air, results are updated in respective branch README using a Linux server
* Demo Video is on non distributed version - [this](https://github.com/kishansairam9/ShardedKVStore/tree/no-distributed) branch

## Table of Contents <!-- omit in toc -->

- [CHANGELOG](#changelog)
- [Problem Statement](#problem-statement)
- [Architecture](#architecture)
- [Replication](#replication)
- [Design Choices](#design-choices)
  - [RAFT Implementation](#raft-implementation)
  - [Interfacing RAFT & Language choice](#interfacing-raft--language-choice)
  - [Data Storage](#data-storage)
- [Implementation](#implementation)
  - [Architecture](#architecture-1)
  - [Files and Directory Structure](#files-and-directory-structure)
  - [Extending implementation to Distributed Setting](#extending-implementation-to-distributed-setting)
- [Documentation](#documentation)
  - [Setup](#setup)
  - [How to Run](#how-to-run)
  - [Handler](#handler)
  - [KVStore Server](#kvstore-server)
  - [Testing](#testing)
  - [Client](#client)
- [Tests / Analysis on distributed version](#tests--analysis-on-distributed-version)
- [Improvements](#improvements)
  - [Making the service also distributed, not just storage](#making-the-service-also-distributed-not-just-storage)
  - [Client side library for faster operations](#client-side-library-for-faster-operations)
  - [Removing lock on each node caused by thread ownership of Pyro5](#removing-lock-on-each-node-caused-by-thread-ownership-of-pyro5)
- [Caveats](#caveats)
- [References](#references)

## CHANGELOG
- 26 Jun 2021 - Added Distributed Support
- 30 Apr 2021 - Initial version with demo video

## Problem Statement

- Key / Value Storage system that "shards," or partitions, the keys over a set of replica groups with read / write support
- RPCs for interaction between clients and servers
- Use PAXOS to replicate shards
    - Upon discussion with TA mentor regarding high complexity of PAXOS implementation and unavailability of trusted open source implementations, we had to look for alternatives
    - We found that RAFT was the only choice available to us to implement the project

## Architecture

- Each shard is a "replica set" and our final key / value store is a set of shards
- The system we are supposed to build is similar in structure to that of Redis operating in cluster mode as shown below

![.images/redis_img.png](.images/redis_img.png)

## Replication

- Using RAFT Algorithm to handle replication. RAFT is primarily a consensus algorithm
- Replication can be posed as consensus algorithm as achieving consensus on operations to perform

## Design Choices

### RAFT Implementation

- Two industry standard implementations available
    - Hasicorp raft [https://github.com/hashicorp/raft](https://github.com/hashicorp/raft) (go)
    - Etcd implementation [https://github.com/etcd-io/etcd](https://github.com/etcd-io/etcd)  (go)
- Upon discussion with TA mentor, we stuck to using Hashicorp as etcd itself is a distributed store and we are implementing a version of distributed store

### Interfacing RAFT & Language choice

- RAFT implementation is in go lang, hence we should use go lang as part of our implementation
- Instead of building entire pipeline in go lang we choose to use Python as our orchestrating language i.e., logic is implemented in Python where as consensus stays in go
- The primary reasons for this is the Exception Handling feature of Python. Since these are multiple moving parts interacting primarily through use of network calls, many different kinds of errors needs to be handled ranging from timeouts, database errors to raft leader issues etc., Thus having flexible error handling reduces complexity of implementation and time
    - Exceptions can be catched at the top in python, i.e., exceptions raised in nested function calls can be catched above
    - Where as in go lang we need to pass errors as return values through every call of function and return them to parent function, exception handling is harder to perform
    - We extensively used custom exceptions and catched them to detect different cases of exceptions, errors and issues encountered

### Data Storage

- Data storage can be done in memory, but we have the following issues
    - Doesn't scale easily as more records means more memory requirements but we might not have that much memory available
    - Recovery issue, with memory based storage we don't have file based recovery except from the consensus algorithm's logs if any (in case of disk based databases we have files written to disk every time thus can recover from it)
- Hence we used Disk backed KV Store at each node due to its advantages over Memory based storage
    - We do have one trade-off which is speed, memory based storage is faster, we have chosen scalability over speed
    - By using disk based store which supports faster access using memory caching we can mitigate this trade-off to some extent
- Utilised [Bitcask](https://github.com/prologic/bitcask). Supports fast access to up to 1M KV Pairs using disk as backing store
- If we want to scale even further to billions of records for each node we should use LevelDB for reasons mentioned [here](https://github.com/prologic/bitcask#is-bitcask-right-for-my-project)
- Since we are already sharding based on key, we stick to using Bitcask as after sharding key space for each node is reduced
- Due to modular implementation, it allows for easy replacement of backing store, primarily `node/fsm.go` has to be modified

## Implementation

### Architecture

- Replication implemented using Raft consensus algorithm (used hashicorp's go implementation)
- Interfaced "node" (each element in replica set) using GRPC from python
- Each "shard" is implemented as a set of nodes taking part in raft consensus
- "KVStore" is implemented as a set of shards

![.images/arch.jpeg](.images/arch.jpeg)

- Distributed architecture is a direct extension of this with a remote handler for node class. (Not shown in image)
- Instead of one node per hanlder we allow it to have multiple nodes. This removes the need for running a new script everytime we want to add a node
- Handler is run on each machine and the set of nodes it corresponds to and operations on them are accessed using RMI. Each handler can have any node of any shard

### Files and Directory Structure

```
.
├── README.md
├── Pipfile <Python Env>
├── Pipfile.lock <Python Env>
├── client.py <Wrapper Client> ||* GRPC Client Wrapper File *||
├── distributed_machine.py <Handler>
├── kvstore_grpc_server.py <KVStore GRPC Server> ||* File to run Server *||
└── test.py <Sanity check and concurrent bechmark script>
├── go_backend
│   ├── go.mod
│   ├── go.sum
│   ├── node <Golang node implementation based on hashicorp raft>
│   │   ├── fsm.go <FSM for raft>
│   │   ├── node_grpc_grpc.pb.go <GRPC generated file>
│   │   ├── node_grpc.pb.go <GRPC generated file>
│   │   └── store.go <Node interface as a KVStore>
│   └── node_grpc_server.go <Golang Node GRPC Server>
├── .images <Images for README>
│   ├── arch.jpeg
│   └── redis_img.png
├── kvstore <Python implementation of Store>
│   ├── internal_node.py <Used by Handler - Node of replica set implemented using GRPC to Golang Node>
│   ├── machines.py <Storage of machine variables and metadata>
│   ├── node.py <Used by Service - Node as RMI call to machine>
│   ├── shard.py <Shard as a replica set of nodes>
│   ├── store.py <Store as a collection of shards>
│   └── utils.py <Custom Exceptions>
├── grpc_utils
│   ├── kvstore_pb2_grpc.py <GRPC Generated files>
│   ├── kvstore_pb2.py <GRPC Generated files>
│   ├── node_grpc_pb2_grpc.py <GRPC Generated files>
│   ├── node_grpc_pb2.py <GRPC Generated files>
│   ├── kvstore.proto <Protobuf for KVStore service>
│   └── node_grpc.proto <Protobuf for Node in Golang>
├── generate_grpc_files.sh <Script for updating protobuf generated files>
├── install_go_backend.sh <Script for installing go backend to local bin>
```

### Extending implementation to Distributed Setting

- Currently we used python's subprocess package to handle spawning and terminating go lang node servers
- Through out implementation every other communication takes place through GPRC and hence can be done over the network as well, enabling easy extension to distributed setting
- To extend our implementation to distributed setting we only need the functionality of doing subprocess calls over the network. This can be done in couple of ways
    1. Use a package that supports distributed spawn and terminate of processes
    2. Create a RPC server on all the other servers we would like to distribute our application over and modify Node class perform operations on remote object rather than local

## Documentation

### Setup

- Install go lang from official site, setup env variables as required for using modules
- Run `install_go_backend.sh` to build binary and symlink it to ~/.local/bin which kvstore programs will refer to
- Install pipenv on your system, and use it to install dependencies from provided Pipfile and then run pipenv shell from repo root to activate virtual env
    - If pipenv complains about specific version 3.9, ignore it and force python version using `-python` flag, any version >=3.7 should work

### How to Run

- Two stages 
    1. Running handler - `distributed_machine.py` 
        - Run `python3 distributed_machine.py` to run handler with default port at 7940
        - NOTE: `install_go_backend.sh` must be done on all machines where `distributed.py` is run
    2. Running store service - `kvstore_grpc_server.py` 
        - Run `python3 kvstore_grpc_server.py <LOG_DIR_LOCATION>` to run GRPC Server for KVStore using default parameters
- All logs are written to `<DIR OF distributed_machine.py RUN>/<LOG_DIR_LOCAATION passed to store>`
- Pass list of `<IP:PORT>`s of machines on which handler is run to service script using `--machines` flag
    - If localhost, pass `0.0.0.0` instead
- Testing / Benchmarking can be done using `test.py` and passing params as required

### Handler

```
usage: distributed_machine.py [-h] [--port PORT] [--storage STORAGE]

KVStore Server Parameters

optional arguments:
  -h, --help         show this help message and exit
  --port PORT        Port of rmi server
  --storage STORAGE  Root dir for storage of this machine's files, defaults to dir from which script is run
```

### KVStore Server

```
usage: kvstore_grpc_server.py [-h] [--port PORT] [--shard_cnt SHARD_CNT] [--replica_cnt REPLICA_CNT] [--max_workers MAX_WORKERS] [--print_req]
                              [--machines MACHINES [MACHINES ...]]
                              storage_loc

KVStore Server Parameters

positional arguments:
  storage_loc           Location storage of all logging and database, inside storage root configuration for each machine

optional arguments:
  -h, --help            show this help message and exit
  --port PORT           Port of grpc server
  --shard_cnt SHARD_CNT
                        No of shards
  --replica_cnt REPLICA_CNT
                        No of replias for each shard
  --max_workers MAX_WORKERS
                        Max workers for grpc threadpool
  --print_req           Print requests as they arive to GRPC Server
  --machines MACHINES [MACHINES ...]
                        Machines in format <IP>(0.0.0.0 for localhost):<PORT> running distributed_machine.py
```

### Testing

```
usage: test.py [-h] [--host HOST] [--port PORT] [--sanity] [--bench_workers BENCH_WORKERS] [--iters ITERS]

KVStore Server Parameters

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           Host
  --port PORT           Port of grpc server
  --sanity              Perform sanity check
  --bench_workers BENCH_WORKERS
                        Workers performing concurrent benchmark
  --iters ITERS         iters
```

### Client

- Clients interact using GRPC, a wrapper `client.py` is provided to handle GRPC requests to server
- Import `RequestWrapper` class from `client.py` and use it to perform interactions with KVStore by passing in location of GRPC Server
- Example run from python3 interpreter at root of repo

```python
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

## Tests / Analysis on distributed version

- Tests / Analysis on non-distributed [version](https://github.com/kishansairam9/ShardedKVStore/tree/no-distributed) are found in it's README [here](https://github.com/kishansairam9/ShardedKVStore/blob/no-distributed/README.md#tests--analysis)
- Direct comparision between these two branches might not be relevant as distributed version has extra network calls for handling each go backend
- As a more accuracte representation we compare between various number of distributed handlers running on different number of machines in this section
- Another tiny difference in tests of both branches is we updated probabilites as 0.5 0.25 0.25 for get put delete respectively, instead of equal probabilites as in general reads are more frequent

- **Sanity Check**
    - Using python dict as reference for correctness, performed all operations with checks for correctness
    - Initially filled database with 10000 entries, later performed another 10000 ops with each probability as
        - 0.15 - put
        - 0.35 - delete
        - 0.4 - get of keys existing in database
        - 0.1 - get of non existing keys in database
- **Concurrent Benchmark** - 10000 operations, get put delete with probabilities of 0.5, 0.25, 0.25


Testing setup
- We used 20 GRPC kvstore service GRPC workers
- All the tests were run on server linux CentOS Server with Xeon Processor. 
- System has 64GB+ RAM (isn't a factor as storage is disk based not in-memory, memory usage was quite low)
- Location on HDD is used for storage

- Note on terminology - here worker means a concurrent user of service. Each worker does 10000 operations
- More number of workers means more no of concurrent operations

5 shards, each with 5 replicas
- On 5 nodes
    - 3m42.067s
- On 3 nodes
    - 3m54.790s
- On 1 node
    - 4m5.963s


Here the difference in time taken for benchmark is only few seconds. These differences are over very small no of machines 1,3,5. 


In practice over much higher scales we can expect more difference in performance. That being said there are critical improvements that can be made to increase performance mentioned in section on [Improvements](#improvements).


For results related to varying shard and replica counts refer tests section of no distributed branch [here](https://github.com/kishansairam9/ShardedKVStore/blob/no-distributed/README.md#tests--analysis)

We can make these following observations in general
- Same number of shards, different number of replicas
    - Consensus algorithm phase dominates more
    - Lower the number of replicas, lower the time
- Different number of shards, same number of replicas
    - Higher number of shards takes lesser time
    - This is because due to sharing of requests among different shards, when we have concurrent operations happening, we get performance advantage
- Higher the number of machines
    - Higher throughput because requests get distributed over all machines

## Improvements


### Making the service also distributed, not just storage
- Current aspect of design which also is a single point of failure & bottleneck is KV Store service
- It runs only on one machine and serves all requests from multiple users
- Issue with running multiple instances of KV Store service is that they need to share state - current details of shards, their locations, leaders etc
- We can tackle this problem of shared state by using a NoSQL database (which is also horizontally scalable) since BASE consistency is enough for this
- Then we can run multiple instances of server and load balance requests among them

### Client side library for faster operations
- In current implementations clients make a call to service and service waits until it gets response for the operation and returns results
- This causes the GRPC server's thread serving request to be busy as long as request is served
- We can do better than this by using a technique similart to GFS where they have a client side library and master routes clients to the specific data location
- So, our service can return the particular node of shard's location to the client and the client side library takes care of remaining
- In case of failures or network partitions when the location returned by service isn't accessible to client, it can communicate to this to service
- Which then falls back to serving the request normal way by fetching the data and passing it back to client
- This increases the ability of service to handle more requests because, it no longer waits for the operation to complete and fetch data
- This improvement can cause resonable speed up with puts and deletes as they have consensus algorithm to complete, which takes more time than a get, all of the time service was waiting previously
- Here as well, in case of failure of puts or delete dut to node not RAFT leader should communicate it to service and fall back to normal way of requests

### Removing lock on each node caused by thread ownership of Pyro5
- Current implementation uses Pyro5 for RMI to distributed nodes. We connect to RMI using Proxy service of Pyro5
- Requirement of Proxy service is the thread invoking the proxy call needs to own the proxy object
- If not we need to claim ownership of Proxy object into current thread to make RMI calls 
- When we are running a GRPC server (with > 1 worker) we have multiple threads invoking requests and thus multiple threads making proxy calls
- To ensure that thread has ownership when it is making a call, we used a lock
- This causes that at any time for any node there is only one request taking place. This can be avoided
- We need to switch from Pyro5 to GRPC for distributed machine calls to make this possible

## Caveats

- Recovery from RAFT logs is tricky, it requires the port mapping to be same as before the crash or shutdown
- On single node it can be achieved by requiring that the old ports are free
- In distributed case it is harder, we need to map the port and node ip as before or else it will fail
- For this reason recovery functionaity is removed in distributed version of implementation
- Single Node version which supports recovery when given same raft ports as before is available on `no-distributed` branch [here](https://github.com/kishansairam9/ShardedKVStore/tree/no-distributed)

## References

- Following repos were referred while implementing replication based on raft consensus
    - [https://github.com/otoolep/hraftd](https://github.com/otoolep/hraftd)
    - [https://github.com/prologic/bitraft](https://github.com/prologic/bitraft)
