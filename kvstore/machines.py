import Pyro5
import Pyro5.api
import threading

Pyro5.config.COMMTIMEOUT = 3
Pyro5.config.MAX_RETRIES = 1

# machines = []
machines_meta = []
# locks = []

def add_machine(host, port):
    global machines_meta
    machines_meta.append((host, port))

def get_machine_lock(idx):
    h, p = machines_meta[idx]
    machine = Pyro5.api.Proxy(f"PYRO:kvstore-machinermi@{h}:{p}")
    machine.store_meta(h,p)
    return machine, threading.Lock()
