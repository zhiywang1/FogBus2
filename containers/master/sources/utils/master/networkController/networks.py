import re
import hashlib
from enum import Enum
from docker import DockerClient
from docker.errors import NotFound


def hash_to_base24(data):
    # Hash the data using SHA-256 and get the hexadecimal output
    hex_hash = hashlib.sha256(data.encode()).hexdigest()
    num = int(hex_hash, 16)
    # Base-36 encoding
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = ''
    while num > 0:
        num, i = divmod(num, 24)
        result = chars[i] + result
    return result


class NetworkStatus(Enum):
    ACTIVE = 'ACTIVE'
    TO_REMOVE = 'TO_REMOVE'


class Network:
    id: str
    request: str
    status: NetworkStatus
    name: str

    def __init__(self,
                 id: str,
                 request: str,
                 status: NetworkStatus,
                 name: str):
        self.id = id
        self.request = request
        self.status = status
        self.name = name


class NetworkController:

    def __init__(self,
                 docker_client: DockerClient):
        self.networks: dict[str, Network] = {}
        self.docker_client = docker_client

    def list_all_networks(self) -> list[Network]:
        networks = self.docker_client.networks.list()
        return networks

    def create_network_for_request(self,
                                   request: str) -> Network:

        network_name = self.generate_network_name(request)
        try:
            self.delete_network(request)
            docker_network = self.docker_client.networks.create(driver='overlay', name=network_name,
                                                                attachable=True)
        except Exception:
            docker_network = self.docker_client.networks.get(network_name)
            pass
        network = Network(id=docker_network.id, request=request, status=NetworkStatus.ACTIVE, name=network_name)
        self.networks[request] = network
        return network

    def connect_container_to_network(self,
                                     container_name,
                                     network_name):
        try:
            network = self.docker_client.networks.get(network_name)
            container = self.docker_client.containers.get(container_name)
            network.connect(container)
        except Exception as e:
            print(e)
            print('The above error is ignored cause it wont affect the functionality')

    def delete_network(self,
                       request: str):
        if request in self.networks:
            del self.networks[request]
        network_name = self.generate_network_name(request)

        try:
            docker_network = self.docker_client.networks.get(network_name)
            docker_network.remove()
        except Exception:
            pass

    @staticmethod
    def generate_network_name(request: str) -> str:
        corrected = re.sub(r"[^a-zA-Z0-9-]", "-", request)
        corrected = corrected.strip("-")
        return hash_to_base24(corrected)

    def init_swarm_manager(self,
                           advertise_addr: str):
        swarm_info = self.docker_client.swarm.attrs
        if swarm_info is not None:
            self.docker_client.swarm.init(advertise_addr=advertise_addr)
            swarm_info = self.docker_client.swarm.attrs

        return swarm_info

    def get_worker_join_token(self):
        swarm_info = self.docker_client.swarm.attrs
        return swarm_info['JoinTokens']['Worker']
