import docker
from utils.common import format_get_request
from twisted.web.resource import Resource
from utils.static.host_config import HostConfig
from utils.static.network_config import NetworkConfig
from utils.static.storage import DiskUsageInfo


class ImageAPIHandler(Resource):
    isLeaf = True

    def __init__(self):
        super().__init__()
        self.docker_client = docker.from_env()

    @format_get_request
    def render_GET(self,
                   data):
        images = self.docker_client.images.list()
        data = {
            "status": "success",
            "data": [image.id for image in images]}
        return data


class StaticAPIHandler(Resource):
    isLeaf = False

    def __init__(self):
        super().__init__()
        self.putChild(b'host-config', HostConfigAPIHandler())
        self.putChild(b'network-config', NetworkConfigAPIHandler())
        self.putChild(b'storage', StorageAPIHandler())
        self.putChild(b'images', ImageAPIHandler())


class HostConfigAPIHandler(Resource):
    isLeaf = True

    @format_get_request
    def render_GET(self,
                   data):
        host_config = HostConfig()
        host_config.get_enabled_users()
        host_config.get_ssh_users()
        host_config.get_sudo_users()
        host_config.get_logged_in_users()
        host_config.get_logged_in_history()
        data = {
            'status': 'success',
            'data': host_config.to_dict()
        }
        return data


class NetworkConfigAPIHandler(Resource):
    isLeaf = True

    @format_get_request
    def render_GET(self,
                   data):
        network_config = NetworkConfig()
        network_config.get_iptables_rules()
        network_config.parse_iptables_rules()
        data = {"status": "success", "data": network_config.to_dict()}
        return data


class StorageAPIHandler(Resource):
    isLeaf = True

    @format_get_request
    def render_GET(self,
                   data):
        storage = DiskUsageInfo()
        storage.get_disk_partitions()
        storage.get_disk_usage()
        data = {"status": "success", "data": storage.to_dict()}
        return data
