# Custom Exceptions
class ReturnedError(Exception):
    pass

class StaleLeader(Exception):
    pass

class GrpcError(Exception):
    pass