import docker

from ..common import ToDict


class ContainerNetwork(ToDict):

    def __init__(self,
                 network_name,
                 ip_address,
                 mac_address,
                 gateway,
                 network_id):
        self.network_name = network_name
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.gateway = gateway
        self.network_id = network_id


class NetworkUtilization(ToDict):

    def __init__(self,
                 interface,
                 rx_bytes,
                 rx_packets,
                 tx_bytes,
                 tx_packets):
        self.interface = interface
        self.rx_bytes = rx_bytes
        self.rx_packets = rx_packets
        self.tx_bytes = tx_bytes
        self.tx_packets = tx_packets


class Container:

    def __init__(self,
                 container_id,
                 container_name,
                 networks,
                 network_usage):
        self.container_id = container_id
        self.container_name = container_name
        self.networks = networks
        self.network_usage = network_usage


class ContainerNetworkUtilization:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.container_networks = []
        self.containers: list[Container] = []

    def fetch_container_networks(self):
        # Get all running containers
        containers = self.docker_client.containers.list()

        for container in containers:
            container_info = {
                "id": container.id,
                "name": container.name,
                "networks": [],
                "network_usage": []
            }

            # Get container's network settings
            network_settings = container.attrs['NetworkSettings']

            # Extract network information
            for network_name, network_info in network_settings['Networks'].items():
                container_info['networks'].append({
                    "network_name": network_name,
                    "ip_address": network_info['IPAddress'],
                    "mac_address": network_info['MacAddress'],
                    "gateway": network_info['Gateway'],
                    "network_id": network_info['NetworkID']
                })

            # Network usage statistics
            stats = container.stats(stream=False)
            networks = stats['networks']

            for iface, iface_stats in networks.items():
                container_info['network_usage'].append({
                    "interface": iface,
                    "rx_bytes": iface_stats['rx_bytes'],
                    "rx_packets": iface_stats['rx_packets'],
                    "tx_bytes": iface_stats['tx_bytes'],
                    "tx_packets": iface_stats['tx_packets']
                })

            self.container_networks.append(container_info)

    def format_container_networks(self):
        self.containers.clear()
        for container in self.container_networks:

            networks = []
            for network in container['networks']:
                networks.append(ContainerNetwork(
                    network['network_name'],
                    network['ip_address'],
                    network['mac_address'],
                    network['gateway'],
                    network['network_id']
                ))

            usages = []
            for usage in container['network_usage']:
                # print(f"Interface: {usage['interface']}")
                # print(f"  RX Bytes: {usage['rx_bytes']}")
                # print(f"  RX Packets: {usage['rx_packets']}")
                # print(f"  TX Bytes: {usage['tx_bytes']}")
                # print(f"  TX Packets: {usage['tx_packets']}")
                usages.append(NetworkUtilization(
                    usage['interface'],
                    usage['rx_bytes'],
                    usage['rx_packets'],
                    usage['tx_bytes'],
                    usage['tx_packets']
                ))
            self.containers.append(
                Container(
                    container['id'],
                    container['name'],
                    networks,
                    usages
                ))

    def to_dict(self):
        return [{
            'container_id': container.container_id,
            'container_name': container.container_name,
            'networks': [network.to_dict() for network in container.networks],
            'network_usage': [usage.to_dict() for usage in container.network_usage]
        } for container in self.containers]


if __name__ == "__main__":
    container_network = ContainerNetworkUtilization()
    container_network.fetch_container_networks()
    container_network.format_container_networks()
