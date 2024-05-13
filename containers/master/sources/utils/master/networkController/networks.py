from enum import Enum
from docker import DockerClient
from docker.errors import NotFound


class NetworkStatus(Enum):
    ACTIVE = 'ACTIVE'
    TO_REMOVE = 'TO_REMOVE'


class Network:
    id: int
    request_id: int
    status: NetworkStatus
    name: str

    def __init__(self,
                 id: int,
                 request_id: int,
                 status: NetworkStatus,
                 name: str):
        self.id = id
        self.request_id = request_id
        self.status = status
        self.name = name


class NetworkController:

    def __init__(self,
                 docker_client: DockerClient):
        self.networks: dict[int, Network] = {}
        self.docker_client = docker_client

    def list_all_networks(self) -> list[Network]:
        networks = self.docker_client.networks.list()
        return networks

    def create_network_for_request(self,
                                   request_id: int) -> Network:
        self.delete_network(request_id)
        network_name = self.generate_network_name(request_id)
        docker_network = self.docker_client.networks.create(driver='overlay', name=network_name,
                                                            attachable=True)
        network = Network(id=docker_network.id, request_id=request_id, status=NetworkStatus.ACTIVE, name=network_name)
        self.networks[request_id] = network
        return network

    def delete_network(self,
                       request_id: int):
        if request_id in self.networks:
            del self.networks[request_id]
        network_name = self.generate_network_name(request_id)

        try:
            docker_network = self.docker_client.networks.get(network_name)
            docker_network.remove()
            if request_id in self.networks:
                del self.networks[request_id]
        except NotFound:
            pass

    @staticmethod
    def generate_network_name(request_id: int) -> str:
        return f'request-{request_id}'
