# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from .import replica_set_pb2 as replica__set__pb2


class ReplicaSetStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Init = channel.unary_unary(
                '/ReplicaSet/Init',
                request_serializer=replica__set__pb2.InitConfig.SerializeToString,
                response_deserializer=replica__set__pb2.OneString.FromString,
                )
        self.Join = channel.unary_unary(
                '/ReplicaSet/Join',
                request_serializer=replica__set__pb2.JoinConfig.SerializeToString,
                response_deserializer=replica__set__pb2.OneString.FromString,
                )
        self.Get = channel.unary_unary(
                '/ReplicaSet/Get',
                request_serializer=replica__set__pb2.OneString.SerializeToString,
                response_deserializer=replica__set__pb2.OneString.FromString,
                )
        self.Put = channel.unary_unary(
                '/ReplicaSet/Put',
                request_serializer=replica__set__pb2.KVPair.SerializeToString,
                response_deserializer=replica__set__pb2.OneString.FromString,
                )
        self.Delete = channel.unary_unary(
                '/ReplicaSet/Delete',
                request_serializer=replica__set__pb2.OneString.SerializeToString,
                response_deserializer=replica__set__pb2.OneString.FromString,
                )
        self.Close = channel.unary_unary(
                '/ReplicaSet/Close',
                request_serializer=replica__set__pb2.OneString.SerializeToString,
                response_deserializer=replica__set__pb2.OneString.FromString,
                )


class ReplicaSetServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Init(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Join(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Put(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Close(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ReplicaSetServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Init': grpc.unary_unary_rpc_method_handler(
                    servicer.Init,
                    request_deserializer=replica__set__pb2.InitConfig.FromString,
                    response_serializer=replica__set__pb2.OneString.SerializeToString,
            ),
            'Join': grpc.unary_unary_rpc_method_handler(
                    servicer.Join,
                    request_deserializer=replica__set__pb2.JoinConfig.FromString,
                    response_serializer=replica__set__pb2.OneString.SerializeToString,
            ),
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=replica__set__pb2.OneString.FromString,
                    response_serializer=replica__set__pb2.OneString.SerializeToString,
            ),
            'Put': grpc.unary_unary_rpc_method_handler(
                    servicer.Put,
                    request_deserializer=replica__set__pb2.KVPair.FromString,
                    response_serializer=replica__set__pb2.OneString.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=replica__set__pb2.OneString.FromString,
                    response_serializer=replica__set__pb2.OneString.SerializeToString,
            ),
            'Close': grpc.unary_unary_rpc_method_handler(
                    servicer.Close,
                    request_deserializer=replica__set__pb2.OneString.FromString,
                    response_serializer=replica__set__pb2.OneString.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ReplicaSet', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ReplicaSet(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Init(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ReplicaSet/Init',
            replica__set__pb2.InitConfig.SerializeToString,
            replica__set__pb2.OneString.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Join(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ReplicaSet/Join',
            replica__set__pb2.JoinConfig.SerializeToString,
            replica__set__pb2.OneString.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ReplicaSet/Get',
            replica__set__pb2.OneString.SerializeToString,
            replica__set__pb2.OneString.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Put(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ReplicaSet/Put',
            replica__set__pb2.KVPair.SerializeToString,
            replica__set__pb2.OneString.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ReplicaSet/Delete',
            replica__set__pb2.OneString.SerializeToString,
            replica__set__pb2.OneString.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Close(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ReplicaSet/Close',
            replica__set__pb2.OneString.SerializeToString,
            replica__set__pb2.OneString.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
