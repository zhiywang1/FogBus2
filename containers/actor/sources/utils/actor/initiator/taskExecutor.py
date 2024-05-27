import hashlib
from os import system
from time import time
from typing import List
from typing import Tuple

from docker.client import DockerClient
from docker.errors import APIError

from .base import BaseInitiator
from ...component.basic import BasicComponent
from ...tools import camelToSnake
from ...tools import filterIllegalCharacter
from ...types import CPU


def hash_to_base36(data):
    # Hash the data using SHA-256 and get the hexadecimal output
    hex_hash = hashlib.sha256(data.encode()).hexdigest()
    num = int(hex_hash, 16)
    # Base-36 encoding
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = ''
    while num > 0:
        num, i = divmod(num, 36)
        result = chars[i] + result
    return result


class TaskExecutorInitiator(BaseInitiator):

    def __init__(
            self,
            basicComponent: BasicComponent,
            isContainerMode: bool,
            dockerClient: DockerClient,
            cpu: CPU):
        BaseInitiator.__init__(
            self,
            basicComponent=basicComponent,
            isContainerMode=isContainerMode,
            dockerClient=dockerClient)
        self.cpu = cpu

    def initTaskExecutor(
            self,
            userID: str,
            userName: str,
            taskName: str,
            taskToken: str,
            childTaskTokens: List[str],
            isContainerMode: bool,
            networkName: str):
        baseTaskName, label = self.covertTaskName(taskName)
        actor = self.basicComponent.me
        master = self.basicComponent.master
        remoteLogger = self.basicComponent.remoteLogger
        childTaskTokens = self.serialize(childTaskTokens)
        if not isContainerMode:
            args = ' --bindIP %s' % actor.addr[0] + \
                   ' --masterIP %s' % master.addr[0] + \
                   ' --masterPort %d' % master.addr[1] + \
                   ' --remoteLoggerIP %s' % remoteLogger.addr[0] + \
                   ' --remoteLoggerPort %d' % remoteLogger.addr[1] + \
                   ' --userID %s' % userID + \
                   ' --taskName %s' % baseTaskName + \
                   ' --taskToken %s' % taskToken + \
                   ' --childrenTaskTokens %s' % childTaskTokens + \
                   ' --actorID %s' % actor.componentID + \
                   ' --totalCPUCores %d' % self.cpu.cores + \
                   ' --cpuFrequency %f' % self.cpu.frequency + \
                   ' --verbose %d' % self.basicComponent.debugLogger.level
            self.initTaskExecutorOnHost(args=args)
            return

        containerName = '%s_%s_%s_%s' % (
            taskName,
            userName,
            actor.nameLogPrinting,
            time())
        containerName = filterIllegalCharacter(string=containerName)
        containerName = hash_to_base36(containerName)
        args = ' --bindIP %s' % containerName + \
               ' --masterIP %s' % master.addr[0] + \
               ' --masterPort %d' % master.addr[1] + \
               ' --remoteLoggerIP %s' % remoteLogger.addr[0] + \
               ' --remoteLoggerPort %d' % remoteLogger.addr[1] + \
               ' --userID %s' % userID + \
               ' --taskName %s' % baseTaskName + \
               ' --taskToken %s' % taskToken + \
               ' --childrenTaskTokens %s' % childTaskTokens + \
               ' --actorID %s' % actor.componentID + \
               ' --totalCPUCores %d' % self.cpu.cores + \
               ' --cpuFrequency %f' % self.cpu.frequency + \
               ' --verbose %d' % self.basicComponent.debugLogger.level
        args += ' --containerName %s' % containerName
        args += ' --networkName %s' % networkName
        args += ' --domainName %s' % self.basicComponent.domainName
        imageName = 'cloudslab/fogbus2-%s:1.0' % camelToSnake(baseTaskName)

        if self.basicComponent.tls_enabled:
            args += ' --enableTLS True'
            args += ' --certFile server.crt'
            args += ' --keyFile  server.key'

        self.initTaskExecutorInContainer(
            imageName=imageName, containerName=containerName, args=args, networkName=networkName)

    def initTaskExecutorOnHost(self,
                               args: str):
        system('cd ../../taskExecutor/sources/ &&'
               ' python taskExecutor.py %s &' % args)
        self.basicComponent.debugLogger.debug(
            'Init TaskExecutor on host:\n %s', args)

    def initTaskExecutorInContainer(
            self,
            args: str,
            imageName: str,
            containerName: str,
            networkName: str):
        try:
            self.dockerClient.containers.run(
                name=containerName,
                detach=True,
                auto_remove=True,
                image=imageName,
                network=networkName,
                working_dir='/workplace',
                volumes={
                    '/var/run/docker.sock':
                        {
                            'bind': '/var/run/docker.sock',
                            'mode': 'rw'}},
                command=args)
            self.basicComponent.debugLogger.debug(
                'Init TaskExecutor in container:\n%s', args)
        except APIError as e:
            if 'cloudslab/' != imageName[:10]:
                return self.initTaskExecutorInContainer(
                    args=args,
                    imageName='cloudslab/' + imageName,
                    containerName=containerName,
                    networkName=networkName)
            self.basicComponent.debugLogger.warning(str(e))

    @staticmethod
    def serialize(childrenTaskTokens: List[str]) -> str:
        if not len(childrenTaskTokens):
            return 'None'
        return ','.join(childrenTaskTokens)

    @staticmethod
    def covertTaskName(taskName: str) -> Tuple[str, str]:
        dashIndex = taskName.find('-')
        if dashIndex == -1:
            label = 'None'
        else:
            label = taskName[dashIndex:]
        baseTaskName = taskName[:dashIndex]
        return baseTaskName, label
