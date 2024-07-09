from docker.client import DockerClient
from docker.errors import APIError

from ..component.basic import BasicComponent
from ..tools import filterIllegalCharacter


class ContainerManager:

    def __init__(
            self,
            basicComponent: BasicComponent,
            containerName: str = '',
            enableOverlay: bool = False):
        self.basicComponent = basicComponent
        self.isContainerMode = True if len(containerName) else False
        self.containerName = containerName
        self.enableOverlay = enableOverlay
        self.dockerClient: DockerClient = DockerClient()

    def tryRenamingContainerName(self, newName: str, previousName: str = ''):
        # not renaming with overlay network due to a bug
        # https://github.com/moby/moby/issues/42351
        return
        newName = filterIllegalCharacter(string=newName)
        if not self.isContainerMode:
            return
        if not newName:
            return
        if not previousName:
            previousName = self.containerName
        if previousName == newName:
            return
        self.tryDeletingContainerByName(newName)
        container = self.dockerClient.containers.get(previousName)
        try:
            container.rename(newName)
            self.containerName = newName
        except APIError:
            self.basicComponent.debugLogger.warning(
                'Failed to rename container as %s', newName)

    def tryDeletingContainerByName(self, containerName: str):
        try:
            container = self.dockerClient.containers.get(containerName)
            container.remove()
            self.basicComponent.debugLogger.warning(
                '%s existed and has been deleted', containerName)
        except APIError:
            pass
