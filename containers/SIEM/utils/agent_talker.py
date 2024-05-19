import requests
import dotenv
import os
from requests.auth import HTTPBasicAuth


class AgentTalker:
    def __init__(self,
                 ip,
                 port,
                 username,
                 password):
        self.base_url = f"http://{ip}:{port}"
        self.auth = HTTPBasicAuth(username, password)

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
        return self._get("static/storage")

    def get_static_network_config(self):
        return self._get("static/network-config")

    def get_static_host_config(self):
        return self._get("static/host-config")

    def get_static_images(self):
        return self._get("static/images")

    def get_dynamic_network_containers(self):
        return self._get("dynamic/network-container")

    def get_dynamic_network_host(self):
        return self._get("dynamic/network-host")

    def get_dynamic_storage(self):
        return self._get("dynamic/storage")

    def get_dynamic_computation(self):
        return self._get("dynamic/computation")

    def get_dynamic_containers(self):
        return self._get("dynamic/containers")

    def post_dynamic_stop_container(self,
                                    container_id):
        return self._post(
            "dynamic/containers",
            {
                "action": "stop",
                "container_id": container_id})


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
