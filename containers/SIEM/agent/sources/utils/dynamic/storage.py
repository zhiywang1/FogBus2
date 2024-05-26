import docker
from ..common import ToDict


class ContainerStorage(ToDict):

    def __init__(self,
                 container_id,
                 container_name,
                 read_bytes,
                 write_bytes,
                 total_bytes):
        self.container_id = container_id
        self.container_name = container_name
        self.read_bytes = read_bytes
        self.write_bytes = write_bytes
        self.total_bytes = total_bytes


class ContainerStorageUtilization:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.container_storages = []

    def fetch_container_storage(self):
        # Get all running containers
        containers = self.docker_client.containers.list()
        self.container_storages.clear()
        for container in containers:
            container_info = ContainerStorage(container_id=container.id,
                                              container_name=container.name,
                                              read_bytes=0,
                                              write_bytes=0,
                                              total_bytes=0)

            stats = container.stats(stream=False)
            blkio_stats = stats['blkio_stats']['io_service_bytes_recursive']
            if blkio_stats is None:
                continue
            for entry in blkio_stats:
                if entry['op'] == 'Read':
                    container_info.read_bytes += entry['value']
                elif entry['op'] == 'Write':
                    container_info.write_bytes += entry['value']

            container_info.total_bytes = container_info.read_bytes + container_info.write_bytes

            self.container_storages.append(container_info)

    def to_dict(self):
        return [container.to_dict() for container in self.container_storages]


if __name__ == "__main__":
    container_storage_util = ContainerStorageUtilization()
    container_storage_util.fetch_container_storage()
    print(container_storage_util.to_dict())
