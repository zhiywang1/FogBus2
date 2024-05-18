from twisted.web.server import Site
from twisted.web.resource import IResource
from twisted.internet import reactor, endpoints
from twisted.web.guard import BasicCredentialFactory, HTTPAuthSessionWrapper, DigestCredentialFactory
from twisted.cred.portal import Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.web.resource import Resource
from zope.interface import implementer

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


@implementer(IResource)
class ProtectedResource(Resource):
    def __init__(self,
                 wrappedResource):
        super().__init__()
        self.wrappedResource = wrappedResource

    def getChild(self,
                 name,
                 request):
        return self.wrappedResource.getChild(name, request)

    def render(self,
               request):
        return self.wrappedResource.render(request)


@implementer(IResource)
class SimpleRealm:
    def __init__(self,
                 resource):
        self.resource = resource

    def requestAvatar(self,
                      avatarId,
                      mind,
                      *interfaces):
        if IResource in interfaces:
            return (IResource, self.resource, lambda: None)
        raise NotImplementedError()


if __name__ == "__main__":
    checker = InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser(b'fogbus2', b'2subgof')
    protected_resource = AgentAPIROOT()

    portal = Portal(SimpleRealm(protected_resource), [checker])

    credentialFactory = BasicCredentialFactory("SIME Agent")
    protected_resource = HTTPAuthSessionWrapper(portal, [credentialFactory])

    endpoint = endpoints.serverFromString(reactor, "tcp:7398")
    factory = Site(protected_resource)
    endpoint.listen(factory)
    print("Agent started on port 7398")
    reactor.run()
