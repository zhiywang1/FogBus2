import argparse
import logging
import os

from utils import BasicComponent
from utils import ComponentRole
from utils import ConfigActor
from utils import ContainerManager
from utils import MessageSubType
from utils import MessageType
from utils import PeriodicTaskRunner
from utils import PeriodicTasks
from utils import ResourcesDiscovery
from utils import terminate
from utils.actor import ActorMessageHandler
from utils.actor import ActorProfiler
from utils.actor import Initiator


class Actor:
    def __init__(
            self,
            addr,
            masterAddr,
            logLevel=logging.DEBUG,
            containerName='',
            enableTLS: bool = False,
            certFile: str = '',
            keyFile: str = '',
            domainName: str = '',
            enableOverlay: bool = False):
        self.basicComponent = BasicComponent(
            ignoreSocketError=True,
            role=ComponentRole.ACTOR,
            addr=addr,
            logLevel=logLevel,
            masterAddr=masterAddr,
            portRange=ConfigActor.portRange,
            enableTLS=enableTLS,
            certFile=certFile,
            keyFile=keyFile,
            domainName=domainName)
        self.resourcesDiscovery = ResourcesDiscovery(
            basicComponent=self.basicComponent)
        self.discoverIfUnset()
        self.containerManager = ContainerManager(
            basicComponent=self.basicComponent,
            containerName=containerName,
            enableOverlay=enableOverlay)
        self.profiler = ActorProfiler(
            basicComponent=self.basicComponent,
            dockerClient=self.containerManager.dockerClient)
        self.initiator: Initiator = Initiator(
            basicComponent=self.basicComponent,
            isContainerMode=self.containerManager.isContainerMode,
            dockerClient=self.containerManager.dockerClient,
            cpu=self.profiler.resources.cpu)
        self.messageHandler = ActorMessageHandler(
            resourcesDiscovery=self.resourcesDiscovery,
            containerManager=self.containerManager,
            basicComponent=self.basicComponent,
            initiator=self.initiator,
            profiler=self.profiler)
        periodicTasks = self.preparePeriodTasks()
        self.periodicTaskRunner = PeriodicTaskRunner(
            basicComponent=self.basicComponent,
            periodicTasks=periodicTasks)

        self.currPath = os.path.abspath(os.path.curdir)

    def discoverIfUnset(self):
        master = self.basicComponent.master
        if master.addr[0] == '' or master.addr[1] == 0:
            self.resourcesDiscovery.discoverAndCommunicate(
                targetRole=ComponentRole.MASTER,
                isNotSetInArgs=True)
        self.resourcesDiscovery.checkPorts()

    def run(self):
        self.register()

    def preparePeriodTasks(self) -> PeriodicTasks:
        periodicTasks = [
            (self.uploadResources, 60),
            (self.uploadImages, 1800)]
        return periodicTasks

    def uploadResources(self):
        self.profiler.profileAll()
        data = {
            'actorResources': self.profiler.resources.toDict()}
        self.basicComponent.sendMessage(
            messageType=MessageType.LOG,
            messageSubType=MessageSubType.HOST_RESOURCES,
            data=data,
            destination=self.basicComponent.master)

    def uploadImages(self):

        data = {
            'images': list(self.profiler.resources.images),
            'runningContainers': list(
                self.profiler.resources.runningContainers)}
        self.basicComponent.sendMessage(
            messageType=MessageType.LOG,
            messageSubType=MessageSubType.CONTAINER_IMAGES_AND_RUNNING_CONTAINERS,
            data=data,
            destination=self.basicComponent.master)

    def register(self):
        self.basicComponent.debugLogger.info('Profiling...')
        self.profiler.profileAll()
        data = {'actorResources': self.profiler.resources.toDict(),
                'domainName': self.basicComponent.domainName}
        self.basicComponent.debugLogger.info('Registering...')
        try:
            self.basicComponent.sendMessage(
                messageType=MessageType.REGISTRATION,
                messageSubType=MessageSubType.REGISTER,
                destination=self.basicComponent.master,
                data=data)
        except OSError:
            self.basicComponent.debugLogger.error(
                'Cannot access Master at %s',
                str(self.basicComponent.master.addr))
            terminate()


def parseArg():
    parser = argparse.ArgumentParser(
        description='Actor')
    parser.add_argument(
        '--bindIP',
        metavar='BindIP',
        type=str,
        help='User ip.')
    parser.add_argument(
        '--bindPort',
        metavar='BindPort',
        nargs='?',
        default=0,
        type=int,
        help='Bind port')
    parser.add_argument(
        '--masterIP',
        metavar='MasterIP',
        type=str,
        help='Master ip.')
    parser.add_argument(
        '--masterPort',
        metavar='MasterPort',
        nargs='?',
        default=0,
        type=int,
        help='Master port')
    parser.add_argument(
        '--containerName',
        metavar='ContainerName',
        nargs='?',
        default='',
        type=str,
        help='container name')
    parser.add_argument(
        '--verbose',
        metavar='Verbose',
        nargs='?',
        default=10,
        type=int,
        help='Reference python logging level, from 0 to 50 integer to show log')
    parser.add_argument(
        '--enableTLS',
        metavar='EnableTLS',
        nargs='?',
        default='',
        type=bool,
        help='enable TLS or not')
    parser.add_argument(
        '--certFile',
        metavar='CertFile',
        nargs='?',
        default='',
        type=str,
        help='Cert file: openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com" ')
    parser.add_argument(
        '--keyFile',
        metavar='keyFile',
        nargs='?',
        default='',
        type=str,
        help='Key file: openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"')
    parser.add_argument(
        '--domainName',
        metavar='domainName',
        nargs='?',
        default='fogbus2',
        type=str,
        help='Domain Name')
    parser.add_argument(
        '--enableOverlay',
        metavar='enableOverlay',
        nargs='?',
        default=False,
        type=bool,
        help='Enable docker overlay or not')

    return parser.parse_args()


if __name__ == '__main__':
    args = parseArg()
    actor_ = Actor(
        addr=(args.bindIP, args.bindPort),
        masterAddr=(args.masterIP, args.masterPort),
        containerName=args.containerName,
        logLevel=args.verbose,
        enableTLS=args.enableTLS,
        certFile=args.certFile,
        keyFile=args.keyFile,
        domainName=args.domainName,
        enableOverlay=args.enableOverlay)
    actor_.run()
