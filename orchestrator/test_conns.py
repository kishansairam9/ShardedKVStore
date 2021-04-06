import sys
sys.path.append('..')
import grpc
from python_grpc import node_grpc_pb2_grpc
from python_grpc import node_grpc_pb2
from time import sleep

channel1 = grpc.insecure_channel('localhost:9000')
channel2 = grpc.insecure_channel('localhost:9005')
channel3 = grpc.insecure_channel('localhost:9010')
stub1 = node_grpc_pb2_grpc.NodeStub(channel1)
stub2 = node_grpc_pb2_grpc.NodeStub(channel2)
stub3 = node_grpc_pb2_grpc.NodeStub(channel3)

# params = {
#     'RaftDir': './testing/raft',
#     'RaftAddr': 'localhost:8005',
#     'StoreDir': './testing/store',
#     'Leader': True,
#     'NodeID': '1'
# }

request = node_grpc_pb2.InitConfig(RaftDir='./testing/raft1', RaftAddr='localhost:8005', StoreDir='./testing/store1', Leader=True, NodeID='1')

print(stub1.Init(request))
sleep(5)

request = node_grpc_pb2.KVPair(Key='abc', Val='xyz')
print(stub1.Put(request))

request = node_grpc_pb2.OneString(Msg='abc')
print(stub1.Get(request))

request = node_grpc_pb2.OneString(Msg='1abc')
print(stub1.Get(request))

request = node_grpc_pb2.InitConfig(RaftDir='./testing/raft2', RaftAddr='localhost:8006', StoreDir='./testing/store2', Leader=True, NodeID='2')

print(stub2.Init(request))
sleep(5)

request = node_grpc_pb2.InitConfig(RaftDir='./testing/raft3', RaftAddr='localhost:8007', StoreDir='./testing/store3', Leader=True, NodeID='3')

print(stub3.Init(request))
sleep(5)

request = node_grpc_pb2.JoinConfig(Addr='localhost:8006', NodeID='2')

print(stub1.Join(request))

request = node_grpc_pb2.JoinConfig(Addr='localhost:8007', NodeID='3')

print(stub1.Join(request))

request = node_grpc_pb2.KVPair(Key='1abc', Val='1xyz')
print(stub1.Put(request))

request = node_grpc_pb2.OneString(Msg='abc')
print(stub2.Get(request))

request = node_grpc_pb2.OneString(Msg='aa1abc')
print(stub2.Get(request))

print("TRY AGAIN ON STUB1")

request = node_grpc_pb2.OneString(Msg='abc')
print(stub1.Get(request))

request = node_grpc_pb2.OneString(Msg='1abc')
print(stub1.Get(request))