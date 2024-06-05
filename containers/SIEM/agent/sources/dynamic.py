import docker
from utils.common import format_get_request, format_post_request
from twisted.web.resource import Resource
from utils.dynamic.computation import ContainerResourceUsage
from utils.dynamic.network_container import ContainerNetworkUtilization
from utils.dynamic.storage import ContainerStorageUtilization
from utils.dynamic.network_host import SSUtilization


class DynamicAPIHandler(Resource):
    isLeaf = False

    def __init__(self):
        super().__init__()
        self.putChild(b'network-container', NetworkAPIHandler())
        self.putChild(b'network-host', HostNetworkAPIHandler())
        self.putChild(b'storage', StorageHandler())
        self.putChild(b'computation', ComputationAPIHandler())
        self.putChild(b'containers', ContainersAPIHandler())


class NetworkAPIHandler(Resource):
    isLeaf = True

    @format_get_request
    def render_GET(self,
                   data):
        network = ContainerNetworkUtilization()
        network.fetch_container_networks()
        network.format_container_networks()
        data = {"status": "success", "data": network.to_dict()}
        return data


class HostNetworkAPIHandler(Resource):
    isLeaf = True

    @format_get_request
    def render_GET(self,
                   data):
        network = SSUtilization()
        network.fetch_connections()
        data = {"status": "success", "data": network.to_dict()}
        return data


class ComputationAPIHandler(Resource):
    isLeaf = True

    @format_get_request
    def render_GET(self,
                   data):
        computation = ContainerResourceUsage()
        computation.get_current_containers_stats()

        data = {"status": "success", "data": computation.to_dict()}
        return data


class StorageHandler(Resource):
    isLeaf = True

    @format_get_request
    def render_GET(self,
                   data):
        storage = ContainerStorageUtilization()
        storage.fetch_container_storage()
        data = {"status": "success", "data": storage.to_dict()}
        return data


class ContainersAPIHandler(Resource):
    isLeaf = True

    def __init__(self):
        super().__init__()
        self.docker_client = docker.from_env()

    @format_get_request
    def render_GET(self,
                   data):
        containers = self.docker_client.containers.list()
        data = {
            "status": "success",
            "data": [{
                "container_id": container.id,
                "image_id": container.image.id} for container in containers],
            "signature_data":
                [{
                    'args': container.attrs['Args'],
                    'container_id': container.id,
                    'container_image_id': container.image.id,
                    'labels': container.labels,
                } for container in containers]
        }
        return data

    @format_post_request
    def render_POST(self,
                    data):
        if "action" not in data:
            return {"status": "error", "message": "Action not found"}
        if "container_id" not in data:
            return {"status": "error", "message": "Container ID not found"}
        if data["action"] == "stop":
            container = self.docker_client.containers.get(data["container_id"])
            container.stop()
            return {
                "status": "success",
                "message": "Container stopped",
                "container_id": data["container_id"]}
        return {"status": "error", "message": "Action not found"}
