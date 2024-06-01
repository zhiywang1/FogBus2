import argparse
import os
from logging import DEBUG

from utils import Address
from utils import BasicComponent
from utils import ComponentRole
from utils import ConfigUser
from utils import ContainerManager
from utils import MessageSubType
from utils import MessageType
from utils import PeriodicTaskRunner
from utils import PeriodicTasks
from utils import ResourcesDiscovery
from utils.user import initActuator
from utils.user import RegistrationManager
from utils.user import UserMessageHandler


class User:

    def __init__(
            self,
            addr: Address,
            masterAddr: Address,
            remoteLoggerAddr: Address,
            appName: str,
            containerName: str = '',
            logLevel=DEBUG,
            enableTLS: bool = False,
            certFile: str = '',
            keyFile: str = '',
            domainName: str = ''):
        self.containerName = containerName
        self.basicComponent = BasicComponent(
            role=ComponentRole.USER,
            addr=addr,
            masterAddr=masterAddr,
            remoteLoggerAddr=remoteLoggerAddr,
            logLevel=logLevel,
            portRange=ConfigUser.portRange,
            enableTLS=enableTLS,
            certFile=certFile,
            keyFile=keyFile,
            domainName=domainName)
        self.resourcesDiscovery = ResourcesDiscovery(
            basicComponent=self.basicComponent)
        self.discoverIfUnset()
        self.containerManager = ContainerManager(
            basicComponent=self.basicComponent,
            containerName=containerName)
        self.registrationManager = RegistrationManager(
            basicComponent=self.basicComponent,
            appName=appName)
        self.actuator = initActuator(
            appName=appName,
            basicComponent=self.basicComponent)
        if self.actuator is None:
            self.basicComponent.debugLogger.error(
                'Application is not supported: %s',
                self.registrationManager.appName)
            os._exit(0)

        self.messageHandler = UserMessageHandler(
            resourcesDiscovery=self.resourcesDiscovery,
            containerManager=self.containerManager,
            basicComponent=self.basicComponent,
            actuator=self.actuator,
            registrationManager=self.registrationManager)
        periodicTasks = self.preparePeriodTasks()
        self.periodicTaskRunner = PeriodicTaskRunner(
            basicComponent=self.basicComponent,
            periodicTasks=periodicTasks)

    def discoverIfUnset(self):
        remoteLogger = self.basicComponent.remoteLogger
        if remoteLogger.addr[0] == '' or remoteLogger.addr[1] == 0:
            self.resourcesDiscovery.discoverAndCommunicate(
                targetRole=ComponentRole.REMOTE_LOGGER,
                isNotSetInArgs=True)
        master = self.basicComponent.master
        if master.addr[0] == '' or master.addr[1] == 0:
            self.resourcesDiscovery.discoverAndCommunicate(
                targetRole=ComponentRole.MASTER,
                isNotSetInArgs=True)
        self.resourcesDiscovery.checkPorts()

    def run(self):
        self.register()

    def register(self):
        self.registrationManager.registerAt(self.basicComponent.master.addr)

    def uploadMedianResponseTime(self):
        responseTime = self.actuator.responseTime.median()
        if responseTime == 0:
            return
        data = {'responseTime': responseTime}
        self.basicComponent.sendMessage(
            messageType=MessageType.LOG,
            messageSubType=MessageSubType.RESPONSE_TIME,
            data=data,
            destination=self.basicComponent.remoteLogger)

    def preparePeriodTasks(self) -> PeriodicTasks:
        periodicTasks = [(self.uploadMedianResponseTime, 10)]
        return periodicTasks


def parseArg():
    parser = argparse.ArgumentParser(
        description='User')
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
        '--remoteLoggerIP',
        metavar='RemoteLoggerIP',
        type=str,
        help='Remote logger ip.')
    parser.add_argument(
        '--remoteLoggerPort',
        metavar='RemoteLoggerPort',
        nargs='?',
        default=0,
        type=int,
        help='Remote logger port')
    parser.add_argument(
        '--applicationName',
        metavar='ApplicationName',
        type=str,
        help='Application Name')

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
        help='Cert file: '
             'openssl req -new -x509 -days 365 -nodes '
             '-out server.crt -keyout server.key '
             '-subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com" ')
    parser.add_argument(
        '--keyFile',
        metavar='keyFile',
        nargs='?',
        default='',
        type=str,
        help='Key file: '
             ''
             'openssl req -new -x509 -days 365 -nodes '
             '-out server.crt -keyout server.key '
             '-subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com" ')
    parser.add_argument(
        '--domainName',
        metavar='domainName',
        nargs='?',
        default='fogbus2',
        type=str,
        help='Domain Name')

    return parser.parse_args()


if __name__ == "__main__":
    args = parseArg()
    user_ = User(
        containerName=args.containerName,
        addr=(args.bindIP, args.bindPort),
        masterAddr=(args.masterIP, args.masterPort),
        remoteLoggerAddr=(args.remoteLoggerIP, args.remoteLoggerPort),
        appName=args.applicationName,
        logLevel=args.verbose,
        enableTLS=args.enableTLS,
        certFile=args.certFile,
        keyFile=args.keyFile,
        domainName=args.domainName)
    user_.run()
