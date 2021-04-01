import grpc
import replica_set_pb2_grpc
import replica_set_pb2
from time import sleep
# from . import replica_set_pb2

channel = grpc.insecure_channel('localhost:9000')
stub = replica_set_pb2_grpc.ReplicaSetStub(channel)

# params = {
#     'RaftDir': './testing/raft',
#     'RaftAddr': 'localhost:8005',
#     'StoreDir': './testing/store',
#     'Leader': True,
#     'NodeID': '1'
# }

request = replica_set_pb2.InitConfig(RaftDir='./testing/raft', RaftAddr='localhost:8005', StoreDir='./testing/store', Leader=True, NodeID='1')

sleep(5)

print(stub.Init(request))

sleep(5)

request = replica_set_pb2.KVPair(Key='abc', Val='xyz')
print(stub.Put(request))

request = replica_set_pb2.OneString(Msg='abc')
print(stub.Get(request))