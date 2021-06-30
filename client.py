import grpc
from grpc_utils import kvstore_pb2, kvstore_pb2_grpc

class RequestWrapper:

    def __init__(self, address: str):
        self.channel = grpc.insecure_channel(address)
        self.stub = kvstore_pb2_grpc.KVStoreStub(self.channel)

    def get(self, key: str):
        request = kvstore_pb2.String(Data=key)
        resp = self.stub.Get(request)
        if resp.Success:
            if resp.Exists:
                return resp.Data
            return None
        print(resp)
        raise Exception(resp.Data)

    def put(self, key: str, val: str):
        request = kvstore_pb2.KeyValuePair(Key=key, Value=val)
        resp = self.stub.Put(request)
        if resp.Success:
            return
        print(resp)
        raise Exception(resp.Data)

    def delete(self, key: str):
        request = kvstore_pb2.String(Data=key)
        resp = self.stub.Delete(request)
        if resp.Success:
            return
        print(resp)
        raise Exception(resp.Data)