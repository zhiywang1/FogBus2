from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor, endpoints
from static import StaticAPIHandler
from dynamic import DynamicAPIHandler


class AgentAPIROOT(Resource):
    isLeaf = False

    def __init__(self):
        super().__init__()
        self.putChild(b'static', StaticAPIHandler())
        self.putChild(b'dynamic', DynamicAPIHandler())

    def render_GET(self,
                   request):
        content = u"SIME Agent is working\n"
        return content.encode("utf-8")

    def getChild(self,
                 name,
                 request):

        if name == b'':
            return self
        return Resource.getChild(self, name, request)


if __name__ == "__main__":
    endpoint = endpoints.serverFromString(reactor, "tcp:7398")
    factory = Site(AgentAPIROOT())
    endpoint.listen(factory)
    print("Agent started on port 7398")
    reactor.run()
