from utils.common import format_request
from twisted.web.resource import Resource
from utils.dynamic.computation import ContainerResourceUsage
from utils.dynamic.network import ContainerNetworkUtilization


class DynamicAPIHandler(Resource):
    isLeaf = False

    def __init__(self):
        super().__init__()
        self.putChild(b'network', NetworkAPIHandler())
        self.putChild(b'storage', StorageHandler())
        self.putChild(b'computation', ComputationAPIHandler())


class NetworkAPIHandler(Resource):
    isLeaf = True

    @format_request
    # TODO
    def render_GET(self,
                   data):
        network = ContainerNetworkUtilization()
        network.fetch_container_networks()
        network.format_container_networks()
        data = {"status": "success", "data": network.to_dict()}
        return data


class ComputationAPIHandler(Resource):
    isLeaf = True

    @format_request
    # TODO
    def render_GET(self,
                   data):
        computation = ContainerResourceUsage()
        computation.get_current_containers_stats()

        data = {"status": "success", "data": computation.to_dict()}
        return data


class StorageHandler(Resource):
    isLeaf = True

    @format_request
    # TODO
    def render_GET(self,
                   data):
        data = {"status": "success"}
        return data
