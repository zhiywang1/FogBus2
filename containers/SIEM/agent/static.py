from utils import check_post_data
from twisted.web.resource import Resource


class StaticAPIHandler(Resource):
    isLeaf = False

    def __init__(self):
        super().__init__()
        self.putChild(b'host-config', HostConfigAPIHandler())
        self.putChild(b'network-config', NetworkConfigAPIHandler())
        self.putChild(b'storage', StorageAPIHandler())
        self.putChild(b'code', CodeAPIHandler())


class HostConfigAPIHandler(Resource):
    isLeaf = True

    @check_post_data
    # TODO
    def render_POST(self,
                    data):
        data = {"status": "success"}
        return data


class NetworkConfigAPIHandler(Resource):
    isLeaf = True

    @check_post_data
    # TODO
    def render_POST(self,
                    data):
        data = {"status": "success"}
        return data


class StorageAPIHandler(Resource):
    isLeaf = True

    @check_post_data
    # TODO
    def render_POST(self,
                    data):
        data = {"status": "success"}
        return data


class CodeAPIHandler(Resource):
    isLeaf = True

    @check_post_data
    # TODO
    def render_POST(self,
                    data):
        data = {"status": "success"}
        return data
