from utils.common import format_request
from twisted.web.resource import Resource


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
        data = {"status": "success"}
        return data


class ComputationAPIHandler(Resource):
    isLeaf = True

    @format_request
    # TODO
    def render_GET(self,
                    data):
        data = {"status": "success"}
        return data


class StorageHandler(Resource):
    isLeaf = True

    @format_request
    # TODO
    def render_GET(self,
                    data):
        data = {"status": "success"}
        return data
