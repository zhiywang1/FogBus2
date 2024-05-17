from utils import check_post_data
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

    @check_post_data
    # TODO
    def render_POST(self,
                    data):
        data = {"status": "success"}
        return data


class ComputationAPIHandler(Resource):
    isLeaf = True

    @check_post_data
    # TODO
    def render_POST(self,
                    data):
        data = {"status": "success"}
        return data


class StorageHandler(Resource):
    isLeaf = True

    @check_post_data
    # TODO
    def render_POST(self,
                    data):
        data = {"status": "success"}
        return data
