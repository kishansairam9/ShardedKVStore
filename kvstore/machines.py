import Pyro5
import Pyro5.api
import threading

Pyro5.config.COMMTIMEOUT = 3
Pyro5.config.MAX_RETRIES = 1

machines = []
machines_meta = []
locks = []

def add_machine(host, port):
    global machines, machines_meta
    machines.append(Pyro5.api.Proxy(f"PYRO:kvstore-machinermi@{host}:{port}"))
    machines_meta.append((host, port))
    machines[-1].store_meta(host, port)
    locks.append(threading.Lock())
