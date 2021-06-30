import random, string, multiprocessing, argparse
from client import RequestWrapper
from time import sleep

def getrandkv(key_len: int, val_len: int):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=key_len)), \
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=val_len))

def sanity_check(address, iters: int, inital_populate: int = 10000):
    """Performs sanity checking of kv store to ensure correctness by using a reference python dictonary"""
    print("Performing SANITY CHECK! Ensure KVStore is empty initally to get correct results, else restart")
    pykv = {}
    req = RequestWrapper(address)
    for _ in range(inital_populate):
        key_len = random.randint(30, 50)
        val_len = random.randint(60, 100)
        k, v = getrandkv(key_len, val_len)
        pykv[k] = v
        req.put(k, v)
    
    for _ in range(iters):
        r = random.random()
        if len(list(pykv.keys()))== 0 or r <= 0.15:
            # Put
            key_len = random.randint(30, 50)
            val_len = random.randint(60, 100)
            k, v = getrandkv(key_len, val_len)
            pykv[k] = v
            req.put(k, v)
        elif r <= 0.5:
            # Delete
            k = random.choice(list(pykv.keys()))
            req.delete(k)
            del pykv[k]
        else:
            # Get
            q = random.random()
            if q <= 0.8:
                k = random.choice(list(pykv.keys()))
                got = req.get(k) 
                if got != pykv[k]:
                    print(f"Get got incorrect result, expected to return <{pykv[k]}> for <{k}> got <{got}> instead")
                    print("Due to BASE consistency, get might have been stale, sleeping 1s and try again")
                    sleep(1)
                    got = req.get(k)
                    assert pykv[k] == got, f"Get got incorrect AFTER ACCOUNTING FOR BASE, expected to return <{pykv[k]}> for <{k}> got <{got}> instead"
                    print("BASE satisfied")
            else:
                k, _ = getrandkv(key_len = random.randint(30, 50), val_len=1)
                if k in pykv:
                    continue
                ret = req.get(k)
                assert ret is None, f"Expected None return as key not present, got <{ret}> intead"
    print("SANITY CHECK SUCCESSFULL")

def worker(idx: int, address: str, iters: int):
    print(f"Worker {idx} started for {iters} iterations")
    req = RequestWrapper(address)
    for _ in range(iters):
        r = random.random()
        key_len = random.randint(30, 50)
        val_len = random.randint(60, 100)
        k, v = getrandkv(key_len, val_len)
        if r < 0.5:
            req.put(k, v)
        elif r < 0.75:
            req.get(k)
        else:
            req.delete(k)
    print(f"Worker {idx} finished {iters} iterations!")


def benchmark(processes: int, address: str, iters: int):
    """Uses multiple processes to benchmark requests"""
    jobs = []
    for i in range(processes):
        p = multiprocessing.Process(target=worker, args=(i, address, iters))
        jobs.append(p)
    for k in jobs:
        k.start()
    for k in jobs:
        k.join()

            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='KVStore Server Parameters')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host')
    parser.add_argument('--port', type=int, default=7000, help='Port of grpc server')
    parser.add_argument('--sanity', action='store_true', help="Perform sanity check")
    parser.add_argument('--bench_workers', type=int, default=5, help='Workers performing concurrent benchmark')
    parser.add_argument('--iters', type=int, default=10000, help='iters')
    args = parser.parse_args()

    addr = f"{args.host}:{args.port}"

    if args.sanity:
        sanity_check(addr, args.iters)
    else:
        benchmark(args.bench_workers, addr, args.iters)
