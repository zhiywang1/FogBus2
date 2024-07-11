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
from utils.user.window import WindowManager
from utils.user.applications import ObjectDetection


class User:

    def __init__(
            self,
            addr: Address,
            masterAddr: Address,
            appName: str,
            windowHeight: int,
            videoPath: str,
            task_count: int,
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
            basicComponent=self.basicComponent,
            window_height=windowHeight,
            video_path=videoPath,
            task_count=task_count
        )
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
        master = self.basicComponent.master
        if master.addr[0] == '' or master.addr[1] == 0:
            self.resourcesDiscovery.discoverAndCommunicate(
                targetRole=ComponentRole.MASTER,
                isNotSetInArgs=True)
        self.resourcesDiscovery.checkPorts()

    def run(self):
        self.register()

    def register(self):
        task_count = None
        if isinstance(self.actuator, ObjectDetection):
            task_count = self.actuator.task_count
        self.registrationManager.registerAt(self.basicComponent.master.addr, task_count)
        if not isinstance(self.actuator, ObjectDetection):
            return
        if not self.actuator.show_window:
            return
        window_manager = WindowManager(
            basicComponent=self.basicComponent,
            frameQueue=self.actuator.window_frame_queue,
            prepareWindows=self.actuator.prepare)
        window_manager.run()

    def uploadMedianResponseTime(self):
        responseTime = self.actuator.responseTime.median()
        if responseTime == 0:
            return
        data = {'responseTime': responseTime}
        self.basicComponent.sendMessage(
            messageType=MessageType.LOG,
            messageSubType=MessageSubType.RESPONSE_TIME,
            data=data,
            destination=self.basicComponent.master)

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
    parser.add_argument(
        '--windowHeight',
        metavar='windowHeight',
        nargs='?',
        default=None,
        type=int,
        help='Window height')
    parser.add_argument(
        '--videoPath',
        metavar='videoPath',
        nargs='?',
        default=None,
        type=str,
        help='Video path')
    parser.add_argument(
        '--taskCount',
        metavar='taskCount',
        nargs='?',
        default=2,
        type=int,
        help='Task count')

    return parser.parse_args()


if __name__ == "__main__":
    args = parseArg()
    user_ = User(
        containerName=args.containerName,
        addr=(args.bindIP, args.bindPort),
        masterAddr=(args.masterIP, args.masterPort),
        appName=args.applicationName,
        logLevel=args.verbose,
        enableTLS=args.enableTLS,
        certFile=args.certFile,
        keyFile=args.keyFile,
        domainName=args.domainName,
        windowHeight=args.windowHeight,
        videoPath=args.videoPath,
        task_count=args.taskCount
    )
    user_.run()
