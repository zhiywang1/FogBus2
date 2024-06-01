import os

from .camelToSnake import camelToSnake
from .base import crossCompileBase


class TaskExecutorImageBuilder:

    def __init__(self):
        containersAbsPath = os.path.abspath(
            __file__[:-len(os.path.basename(__file__))])
        self.dockerFilesFolder = os.path.join(
            containersAbsPath,
            '..%s..%s..%scontainers' % (os.sep, os.sep, os.sep),
            'taskExecutor%sdockerFiles' % os.sep)

    def build(
            self,
            image_tag,
            proxy: str = None,
            platforms: str = '',
            dockerHubUsername: str = '',
            push: bool = False) -> int:
        # get the parentfolder name
        parentFolder = os.path.abspath(os.path.join(self.dockerFilesFolder, '..'))
        more_folder = []
        for folder in os.listdir(parentFolder):
            if folder not in {'dockerFiles', 'sources'}:
                more_folder.append(folder)
        more_folder += os.listdir(self.dockerFilesFolder)
        for folder in more_folder:
            folderAbsPath = os.path.join(self.dockerFilesFolder, folder)
            composeFilepath = os.path.join(folderAbsPath, 'docker-compose.yml')
            if not os.path.exists(composeFilepath):
                continue
            # copy sources folder
            os.system('cp -r %s/../../sources %s/sources' % (
                folderAbsPath, folderAbsPath))
            if platforms != '':
                ret = self.crossCompile(
                    image_tag=image_tag,
                    composeFolder=folderAbsPath,
                    proxy=proxy,
                    platforms=platforms,
                    dockerHubUsername=dockerHubUsername,
                    push=push)
            else:
                command = 'cd %s && docker-compose build' % folderAbsPath

                if proxy is not None:
                    command += ' --build-arg http_proxy=%s' % proxy + \
                               ' --build-arg https_proxy=%s' % proxy
                ret = os.system(
                    'cd %s && docker-compose build' % folderAbsPath)
            # delete sources folder
            os.system('rm -rf %s/sources' % folderAbsPath)

            if ret != 0:
                raise Exception('Failed to build: %s' % composeFilepath)
        return 0

    @staticmethod
    def crossCompile(
            image_tag: str,
            composeFolder: str,
            proxy: str = None,
            platforms: str = 'linux/amd64,'
                             'linux/arm64,'
                             'linux/arm/v7,'
                             'linux/arm/v6',
            dockerHubUsername: str = '',
            push: bool = False):
        return crossCompileBase(
            image_tag=image_tag,
            composeFolder=composeFolder,
            proxy=proxy,
            platforms=platforms,
            dockerHubUsername=dockerHubUsername,
            push=push)


if __name__ == '__main__':
    builder = TaskExecutorImageBuilder()
    builder.build()
