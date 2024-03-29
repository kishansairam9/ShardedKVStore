import argparse
import grpc
from concurrent import futures
from grpc_utils import kvstore_pb2_grpc, kvstore_pb2
from kvstore.store import Store

class KVStoreServicer(kvstore_pb2_grpc.KVStoreServicer):

    def __init__(self, shard_cnt, replica_cnt, storage_loc, machines, print_req):
        self.print_req = print_req 
        self.store = Store(shard_cnt, replica_cnt, storage_loc, machines)

    def Get(self, request, context):
        if self.print_req:
            print(f"GRPC server got Get('{request.Data}')")
        succ, ret = self.store.get(request.Data)
        return kvstore_pb2.ValueReturn(Success=succ, Exists=(ret != None), Data='' if ret == None else ret)

    def Put(self, request, context):
        if self.print_req:
            print(f"GRPC server got Put('{request.Key}', '{request.Value}')")
        succ, ret = self.store.put(request.Key, request.Value)
        return kvstore_pb2.Status(Success=succ, Error='' if ret == None else ret)

    def Delete(self, request, context):
        if self.print_req:
            print(f"GRPC server got Delete('{request.Data}')")
        succ, ret = self.store.delete(request.Data)
        return kvstore_pb2.Status(Success=succ, Error='' if ret == None else ret)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KVStore Server Parameters')
    parser.add_argument('storage_loc', help='Location storage of all logging and database, inside storage root configuration for each machine')
    parser.add_argument('--port', type=int, default=7000, help='Port of grpc server')
    parser.add_argument('--shard_cnt', type=int, default=5, help='No of shards')
    parser.add_argument('--replica_cnt', type=int, default=5, help='No of replias for each shard')
    parser.add_argument('--max_workers', type=int, default=10, help='Max workers for grpc threadpool')
    parser.add_argument('--print_req', action='store_true', help="Print requests as they arive to GRPC Server")
    parser.add_argument("--machines", nargs="+", default=["0.0.0.0:7940"], help="Machines in format <IP>(0.0.0.0 for localhost):<PORT> running distributed_machine.py")
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=args.max_workers))
    kvstore_pb2_grpc.add_KVStoreServicer_to_server(KVStoreServicer(args.shard_cnt, args.replica_cnt, args.storage_loc, args.machines, args.print_req), server)
    server_addr = f'0.0.0.0:{args.port}'
    server.add_insecure_port(server_addr)
    server.start()
    print(f"GRPC Server started at {server_addr}")
    server.wait_for_termination()