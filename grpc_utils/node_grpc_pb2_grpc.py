# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from grpc_utils import node_grpc_pb2 as grpc__utils_dot_node__grpc__pb2


class NodeStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Init = channel.unary_unary(
                '/Node/Init',
                request_serializer=grpc__utils_dot_node__grpc__pb2.InitConfig.SerializeToString,
                response_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                )
        self.Join = channel.unary_unary(
                '/Node/Join',
                request_serializer=grpc__utils_dot_node__grpc__pb2.JoinConfig.SerializeToString,
                response_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                )
        self.Get = channel.unary_unary(
                '/Node/Get',
                request_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
                response_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                )
        self.Put = channel.unary_unary(
                '/Node/Put',
                request_serializer=grpc__utils_dot_node__grpc__pb2.KVPair.SerializeToString,
                response_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                )
        self.Delete = channel.unary_unary(
                '/Node/Delete',
                request_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
                response_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                )
        self.Close = channel.unary_unary(
                '/Node/Close',
                request_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
                response_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                )
        self.IsLeader = channel.unary_unary(
                '/Node/IsLeader',
                request_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
                response_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                )


class NodeServicer(object):
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

    def IsLeader(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NodeServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Init': grpc.unary_unary_rpc_method_handler(
                    servicer.Init,
                    request_deserializer=grpc__utils_dot_node__grpc__pb2.InitConfig.FromString,
                    response_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            ),
            'Join': grpc.unary_unary_rpc_method_handler(
                    servicer.Join,
                    request_deserializer=grpc__utils_dot_node__grpc__pb2.JoinConfig.FromString,
                    response_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            ),
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                    response_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            ),
            'Put': grpc.unary_unary_rpc_method_handler(
                    servicer.Put,
                    request_deserializer=grpc__utils_dot_node__grpc__pb2.KVPair.FromString,
                    response_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                    response_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            ),
            'Close': grpc.unary_unary_rpc_method_handler(
                    servicer.Close,
                    request_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                    response_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            ),
            'IsLeader': grpc.unary_unary_rpc_method_handler(
                    servicer.IsLeader,
                    request_deserializer=grpc__utils_dot_node__grpc__pb2.OneString.FromString,
                    response_serializer=grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Node', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Node(object):
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
        return grpc.experimental.unary_unary(request, target, '/Node/Init',
            grpc__utils_dot_node__grpc__pb2.InitConfig.SerializeToString,
            grpc__utils_dot_node__grpc__pb2.OneString.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/Node/Join',
            grpc__utils_dot_node__grpc__pb2.JoinConfig.SerializeToString,
            grpc__utils_dot_node__grpc__pb2.OneString.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/Node/Get',
            grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            grpc__utils_dot_node__grpc__pb2.OneString.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/Node/Put',
            grpc__utils_dot_node__grpc__pb2.KVPair.SerializeToString,
            grpc__utils_dot_node__grpc__pb2.OneString.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/Node/Delete',
            grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            grpc__utils_dot_node__grpc__pb2.OneString.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/Node/Close',
            grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            grpc__utils_dot_node__grpc__pb2.OneString.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def IsLeader(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Node/IsLeader',
            grpc__utils_dot_node__grpc__pb2.OneString.SerializeToString,
            grpc__utils_dot_node__grpc__pb2.OneString.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
