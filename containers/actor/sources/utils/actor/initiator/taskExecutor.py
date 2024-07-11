import hashlib
import json
import sys
import os
from os import system
from time import time
from typing import List
from typing import Tuple

from docker.client import DockerClient

from .base import BaseInitiator
from ...component.basic import BasicComponent
from ...tools import camelToSnake
from ...tools import filterIllegalCharacter
from ...types import CPU
from ...config import ConfigTaskExecutor


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
        self.port = ConfigTaskExecutor.portRange[0]

    def initTaskExecutor(
            self,
            userID: str,
            userName: str,
            taskName: str,
            taskToken: str,
            childTaskTokens: List[str],
            isContainerMode: bool,
            networkName: str,
            signedAttributes: list,
            signature: str):
        baseTaskName, label = self.covertTaskName(taskName)
        actor = self.basicComponent.me
        master = self.basicComponent.master
        childTaskTokens = self.serialize(childTaskTokens)
        args = ''
        args += ' --domainName %s' % self.basicComponent.domainName
        if self.port >= ConfigTaskExecutor.portRange[1]:
            self.basicComponent.debugLogger.warning("Task Executor Port out of range")
            self.port = ConfigTaskExecutor.portRange[0]
        args += ' --bindPort %d' % self.port
        self.port += 1

        if self.basicComponent.tls_enabled:
            args += ' --enableTLS True'
            args += ' --certFile server.crt'
            args += ' --keyFile  server.key'
        if not isContainerMode:
            args += ' --bindIP %s' % actor.addr[0] + \
                    ' --masterIP %s' % master.addr[0] + \
                    ' --masterPort %d' % master.addr[1] + \
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
        args += ' --bindIP %s' % containerName + \
                ' --masterIP %s' % master.addr[0] + \
                ' --masterPort %d' % master.addr[1] + \
                ' --userID %s' % userID + \
                ' --taskName %s' % baseTaskName + \
                ' --taskToken %s' % taskToken + \
                ' --childrenTaskTokens %s' % childTaskTokens + \
                ' --actorID %s' % actor.componentID + \
                ' --totalCPUCores %d' % self.cpu.cores + \
                ' --cpuFrequency %f' % self.cpu.frequency + \
                ' --verbose %d' % self.basicComponent.debugLogger.level
        args += ' --containerName %s' % containerName
        if networkName:
            args += ' --networkName %s' % networkName
        if baseTaskName.startswith('ObjectDetectionYolov7'):
            baseTaskName = 'ObjectDetectionYolov7'
        imageName = 'cloudslab/fogbus2-%s:1.0' % camelToSnake(baseTaskName)

        self.initTaskExecutorInContainer(
            imageName=imageName,
            containerName=containerName,
            args=args,
            networkName=networkName,
            signedAttributes=signedAttributes,
            signature=signature)

    def initTaskExecutorOnHost(self,
                               args: str):
        script_path = os.path.dirname(os.path.abspath(__file__))
        yolo_path = os.path.abspath(os.path.join(script_path, '../../taskExecutor/sources/utils/taskExecutor/tasks'))
        sys.path.insert(0, yolo_path)
        self.basicComponent.debugLogger.info(args)
        # system(f'export PYTHONPATH={yolo_path}:$PYTHONPATH'
        #        ' && cd ../../taskExecutor/sources/'
        #        f'&& python -m memory_profiler taskExecutor.py {args} &')
        system(f'export PYTHONPATH={yolo_path}:$PYTHONPATH'
               ' && cd ../../taskExecutor/sources/'
               f'&& python taskExecutor.py {args} &')
        self.basicComponent.debugLogger.debug(
            'Init TaskExecutor on host:\n %s', args)

    def initTaskExecutorInContainer(
            self,
            args: str,
            imageName: str,
            containerName: str,
            networkName: str,
            signedAttributes: list,
            signature: str):
        signedAttributes = json.dumps(signedAttributes)

        labels = {
            'signedAttributes': signedAttributes,
            'signature': signature
        }
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
            command=args,
            labels=labels)
        self.basicComponent.debugLogger.debug(
            'Init TaskExecutor in container:\n%s', args)

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
