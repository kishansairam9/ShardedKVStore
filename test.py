import random, string, multiprocessing
from client import RequestWrapper

def getrandkv(key_len: int, val_len: int):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=key_len)), \
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=val_len))

def sanity_check(address, iters: int, inital_populate: int = 1000):
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
        if r <= 0.15:
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
                assert pykv[k] == req.get(k), f"Get got incorrect result, expected to return <{pykv[k]}> for <{k}> got <{req.get(k)}> instead"
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
        if r < 0.33:
            req.put(k, v)
        elif r < 0.66:
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
    # sanity_check('localhost:7000', 1000)
    benchmark(20, 'localhost:7000', 10000)