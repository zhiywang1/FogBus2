import argparse
import logging
import threading
from typing import List

from utils import BasicComponent
from utils import ComponentRole
from utils import ConfigTaskExecutor
from utils import ContainerManager
from utils import MessageSubType
from utils import MessageType
from utils import PeriodicTaskRunner
from utils import PeriodicTasks
from utils import terminate
from utils.taskExecutor.tasks.base import BaseTask
from utils.taskExecutor import initTask
from utils.taskExecutor import RegistrationManager
from utils.taskExecutor import ResourcesProfiler
from utils.taskExecutor import TaskExecutorMessageHandler


class TaskExecutor:

    def __init__(
            self,
            addr,
            masterAddr,
            userID: str,
            taskName: str,
            taskToken: str,
            childTaskTokens: List[str],
            actorID: str,
            totalCPUCores: int,
            cpuFreq: float,
            containerName: str = '',
            networkName: str = '',
            logLevel=logging.DEBUG,
            enableTLS: bool = False,
            certFile: str = '',
            keyFile: str = '',
            domainName: str = ''):
        self.basicComponent = BasicComponent(
            role=ComponentRole.TASK_EXECUTOR,
            addr=addr,
            masterAddr=masterAddr,
            logLevel=logLevel,
            portRange=ConfigTaskExecutor.portRange,
            enableTLS=enableTLS,
            certFile=certFile,
            keyFile=keyFile,
            domainName=domainName)
        self.task: BaseTask = initTask(taskName)
        if self.task is None:
            self.basicComponent.debugLogger.error(
                'TaskName invalid: %s', taskName)
            terminate()
            return
        self.containerName = containerName
        self.networkName = networkName
        self.registrationManager = RegistrationManager(
            basicComponent=self.basicComponent,
            userID=userID,
            actorID=actorID,
            taskName=taskName,
            taskToken=taskToken,
            childrenTaskTokens=childTaskTokens,
            totalCPUCores=totalCPUCores,
            cpuFreq=cpuFreq)
        self.containerManager = ContainerManager(
            basicComponent=self.basicComponent,
            containerName=containerName,
            networkName=networkName
        )

        self.profiler = ResourcesProfiler(
            basicComponent=self.basicComponent,
            resources=self.task.medianProcessingTime.resources)
        self.resetEvent: threading.Event = threading.Event()

        self.messageHandler = TaskExecutorMessageHandler(
            containerManager=self.containerManager,
            basicComponent=self.basicComponent,
            task=self.task,
            registrationManager=self.registrationManager)
        periodicTasks = self.preparePeriodTasks()
        self.periodicTaskRunner = PeriodicTaskRunner(
            basicComponent=self.basicComponent,
            periodicTasks=periodicTasks)

    def updateResources(self):
        self.profiler.profileResources()

    def uploadMedianProcessTime(self):
        if self.task.medianProcessingTime.processingTime == .0:
            return
        data = {'medianProcessTime': self.task.medianProcessingTime.toDict()}
        self.basicComponent.sendMessage(
            messageType=MessageType.LOG,
            messageSubType=MessageSubType.MEDIAN_PROCESSING_TIME,
            data=data,
            destination=self.basicComponent.master)

    def run(self):
        self.register()

    def register(self):
        self.registrationManager.registerAt(
            userID=self.registrationManager.userID,
            taskName=self.registrationManager.taskName,
            taskToken=self.registrationManager.taskToken,
            masterAddr=self.basicComponent.master.addr)
        self.basicComponent.isRegistered.wait()
        self.basicComponent.debugLogger.debug("Registered.")

    def preparePeriodTasks(self) -> PeriodicTasks:
        periodicTasks = [
            (self.uploadMedianProcessTime, 30),
            (self.updateResources, 60)]
        return periodicTasks


def parseArg():
    parser = argparse.ArgumentParser(
        description='TaskExecutor')
    parser.add_argument(
        '--bindIP',
        metavar='BindIP',
        type=str,
        help='TaskExecutor ip.')
    parser.add_argument(
        '--bindPort',
        metavar='BindPort',
        nargs='?',
        default=0,
        type=int,
        help='Bind port')
    parser.add_argument(
        '--network',
        metavar='docker network',
        type=str,
        help='The network this container will use')
    parser.add_argument(
        '--masterIP',
        metavar='MasterIP',
        type=str,
        help='Master ip.')
    parser.add_argument(
        '--masterPort',
        metavar='MasterPort',
        type=int,
        help='Master port')
    parser.add_argument(
        '--userID',
        metavar='UserID',
        type=str,
        help='User id.')
    parser.add_argument(
        '--taskName',
        metavar='TaskName',
        type=str,
        help='Task name.')
    parser.add_argument(
        '--taskToken',
        metavar='TaskToken',
        type=str,
        help='Task token.')
    parser.add_argument(
        '--childrenTaskTokens',
        metavar='ChildrenTaskTokens',
        type=str,
        help='Children task token. E.g. token0,token1,token2')
    parser.add_argument(
        '--actorID',
        metavar='ActorID',
        type=str,
        help='Actor id.')
    parser.add_argument(
        '--totalCPUCores',
        metavar='TotalCPUCores',
        type=int,
        help='cpu cores count')
    parser.add_argument(
        '--cpuFrequency',
        metavar='CPUFrequency',
        type=float,
        help='cpu frequency')
    parser.add_argument(
        '--verbose',
        metavar='Verbose',
        nargs='?',
        default=10,
        type=int,
        help='Reference python logging level, from 0 to 50 integer to show log')
    parser.add_argument(
        '--containerName',
        metavar='ContainerName',
        nargs='?',
        default='',
        type=str,
        help='container name')
    parser.add_argument(
        '--networkName',
        metavar='networkName',
        nargs='?',
        default='',
        type=str,
        help='networkName')
    parser.add_argument(
        '--enableTLS',
        metavar='EnableTLS',
        nargs='?',
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

    return parser.parse_args()


if __name__ == '__main__':
    args = parseArg()
    if args.childrenTaskTokens == 'None':
        args.childrenTaskTokens = []
    elif isinstance(args.childrenTaskTokens, str):
        args.childrenTaskTokens = args.childrenTaskTokens.split(',')
    taskExecutor_ = TaskExecutor(
        containerName=args.containerName,
        networkName=args.networkName,
        addr=(args.bindIP, args.bindPort),
        masterAddr=(args.masterIP, args.masterPort),
        userID=args.userID,
        taskName=args.taskName,
        taskToken=args.taskToken,
        childTaskTokens=args.childrenTaskTokens,
        actorID=args.actorID,
        totalCPUCores=args.totalCPUCores,
        cpuFreq=args.cpuFrequency,
        logLevel=args.verbose,
        enableTLS=args.enableTLS,
        certFile=args.certFile,
        keyFile=args.keyFile,
        domainName=args.domainName)
    taskExecutor_.run()
