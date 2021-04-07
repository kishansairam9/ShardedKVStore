import argparse
import grpc
from concurrent import futures
from python_grpc import kvstore_pb2_grpc, kvstore_pb2
from kvstore.store import Store

class KVStoreServicer(kvstore_pb2_grpc.KVStoreServicer):

    def __init__(self, shard_cnt, replica_cnt, storage_loc):
        self.store = Store(shard_cnt, replica_cnt, storage_loc)

    def Get(self, request, context):
        print(f"GRPC server got Get({request.Data})")
        succ, ret = self.store.get(request.Data)
        return kvstore_pb2.ValueReturn(Success=succ, Exists=(ret != None), Data='' if ret == None else ret)

    def Put(self, request, context):
        print(f"GRPC server got Put({request.Key}, {request.Value})")
        succ, ret = self.store.put(request.Key, request.Value)
        return kvstore_pb2.Status(Success=succ, Error='' if ret == None else ret)

    def Delete(self, request, context):
        print(f"GRPC server got Delete({request.Data})")
        succ, ret = self.store.delete(request.Data)
        return kvstore_pb2.Status(Success=succ, Error='' if ret == None else ret)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KVStore Server Parameters')
    parser.add_argument('storage_loc', help='Location for storage of all logging and database')
    parser.add_argument('--port', type=int, default=7000, help='Port of grpc server')
    parser.add_argument('--shard_cnt', type=int, default=5, help='No of shards')
    parser.add_argument('--replica_cnt', type=int, default=5, help='No of replias for each shard')
    parser.add_argument('--max_workers', type=int, default=10, help='Max workers for grpc threadpool')
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=args.max_workers))
    kvstore_pb2_grpc.add_KVStoreServicer_to_server(KVStoreServicer(args.shard_cnt, args.replica_cnt, args.storage_loc), server)
    server_addr = f'localhost:{args.port}'
    print(f"GRPC Server started at {server_addr}")
    server.add_insecure_port(server_addr)
    server.wait_for_termination()