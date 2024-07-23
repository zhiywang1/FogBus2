import argparse

import dotenv
import os
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


def parse_arg():
    parser = argparse.ArgumentParser(
        description='SIEM-Agent')
    parser.add_argument(
        '--port',
        metavar='Port',
        nargs='?',
        default=7398,
        type=int,
        help='Port number.')
    return parser.parse_args()


if __name__ == "__main__":
    dotenv.load_dotenv()
    username = os.getenv("AGENT_BASIC_HTTP_USER")
    password = os.getenv("AGENT_BASIC_HTTP_PASS")
    checker = InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser(username.encode('utf-8'), password.encode('utf-8'))
    protected_resource = AgentAPIROOT()

    portal = Portal(SimpleRealm(protected_resource), [checker])

    credentialFactory = BasicCredentialFactory("SIME Agent")
    protected_resource = HTTPAuthSessionWrapper(portal, [credentialFactory])
    # "tcp:80:interface=127.0.0.1"
    args = parse_arg()
    endpoint = endpoints.serverFromString(reactor, f"tcp:{args.port}:interface=0.0.0.0")
    factory = Site(protected_resource)
    endpoint.listen(factory)
    print(f"[*] Listen on all address at port {args.port}")
    reactor.run()
