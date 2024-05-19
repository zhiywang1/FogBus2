import requests
import dotenv
import os
from requests.auth import HTTPBasicAuth
from .audit_logger import FileAuditLogger


class AgentTalker:
    def __init__(self,
                 ip,
                 port,
                 username,
                 password):
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.auth = HTTPBasicAuth(username, password)
        self.audit_logger = FileAuditLogger(f'logs/{ip}-{port}')

    def _get(self,
             path):
        try:
            response = requests.get(f"{self.base_url}/{path}", auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def _post(self,
              path,
              data):
        try:
            response = requests.post(f"{self.base_url}/{path}", json=data, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_static_storage(self):
        path = "static/storage"
        resp = self._get(path)
        self.audit_logger.log(resp, file_path=path)
        return resp

    def get_static_network_config(self):
        path = "static/network-config"
        resp = self._get(path)
        self.audit_logger.log(resp, file_path=path)
        return resp

    def get_static_host_config(self):
        path = "static/host-config"
        resp = self._get(path)
        self.audit_logger.log(resp, file_path=path)
        return resp

    def get_static_images(self):
        path = "static/images"
        resp = self._get(path)
        self.audit_logger.log(resp, file_path=path)
        return resp

    def get_dynamic_network_containers(self):
        path = "dynamic/network-container"
        resp = self._get(path)
        self.audit_logger.log(resp, file_path=path)
        return resp

    def get_dynamic_network_host(self):
        path = "dynamic/network-host"
        resp = self._get(path)
        self.audit_logger.log(resp, file_path=path)
        return resp

    def get_dynamic_storage(self):
        path = "dynamic/storage"
        resp = self._get(path)
        self.audit_logger.log(resp, file_path=path)
        return resp

    def get_dynamic_computation(self):
        path = "dynamic/computation"
        resp = self._get(path)
        self.audit_logger.log(resp, file_path=path)
        return resp

    def get_dynamic_containers(self):
        path = "dynamic/containers"
        resp = self._get(path)
        self.audit_logger.log(resp, file_path=path)
        return resp

    def post_dynamic_stop_container(self,
                                    container_id):
        path = "dynamic/containers"
        payload = {
            "action": "stop",
            "container_id": container_id
        }
        resp = self._post(path, payload)
        self.audit_logger.log(resp, file_path=path)
        return resp


if __name__ == "__main__":
    dotenv.load_dotenv()
    hostname = os.getenv("AGENT_HOSTNAME")
    port = int(os.getenv("AGENT_PORT"))
    username = os.getenv("AGENT_BASIC_HTTP_USER")
    password = os.getenv("AGENT_BASIC_HTTP_PASS")
    agent_talker = AgentTalker(hostname, port, username, password)

    print(agent_talker.get_static_host_config())
    print(agent_talker.get_static_network_config())
    print(agent_talker.get_static_storage())
    print(agent_talker.get_static_images())
    print(agent_talker.get_dynamic_network_containers())
    print(agent_talker.get_dynamic_network_host())
    print(agent_talker.get_dynamic_storage())
    print(agent_talker.get_dynamic_computation())
    print(agent_talker.get_dynamic_containers())
    print(agent_talker.post_dynamic_stop_container("89d79f69ae"))
