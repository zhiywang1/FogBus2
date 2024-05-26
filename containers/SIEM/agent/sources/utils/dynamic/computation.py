import docker
from ..common import ToDict


class Container(ToDict):

    def __init__(self,
                 raw_stats,
                 container_id,
                 name,
                 cpu_percent,
                 cpu_delta,
                 system_cpu_delta,
                 number_cpus,
                 memory_utilization,
                 memory_total,
                 network_in,
                 network_out,
                 block_in,
                 block_out):
        self.raw_stats = str(raw_stats)
        self.id = container_id
        self.name = name
        self.cpu_percent = cpu_percent
        self.cpu_delta = cpu_delta
        self.system_cpu_delta = system_cpu_delta
        self.number_cpus = number_cpus
        self.memory_utilization = memory_utilization
        self.memory_total = memory_total
        self.network_in = network_in
        self.network_out = network_out
        self.block_in = block_in
        self.block_out = block_out


class ContainerResourceUsage:
    def __init__(self):
        self.client = docker.from_env()
        self.containers: list[Container] = []
        self.containers_stats = []

    def get_current_containers_stats(self):
        containers = self.client.containers.list()
        self.containers_stats.clear()
        for container in containers:
            stats = container.stats(stream=False)
            self.containers_stats.append(stats)
        self.format_stats()

    def calculate_cpu_percent(self,
                              stats):
        cpu_delta = self.get_cpu_delta(stats)
        system_cpu_delta = self.get_cpu_total(stats)
        number_cpus = self.get_num_cpus(stats)
        if system_cpu_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_cpu_delta) * number_cpus * 100.0
        else:
            cpu_percent = 0.0
        return cpu_percent

    @staticmethod
    def get_cpu_delta(
            stats):
        return stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']

    @staticmethod
    def get_cpu_total(stats):
        system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']

        return system_cpu_delta

    @staticmethod
    def get_num_cpus(stats):
        return stats['precpu_stats']['online_cpus']

    @staticmethod
    def calculate_memory_usage(
            stats):
        mem_usage = stats['memory_stats']['usage']
        mem_limit = stats['memory_stats']['limit']
        mem_percent = (mem_usage / mem_limit) * 100.0
        return {'usage': mem_usage, 'limit': mem_limit, 'percent': mem_percent}

    @staticmethod
    def calculate_network_io(stats):
        network_stats = stats.get('networks', {})
        if not network_stats:
            return {'rx_bytes': 0, 'tx_bytes': 0}
        rx_bytes = sum(interface['rx_bytes'] for interface in network_stats.values())
        tx_bytes = sum(interface['tx_bytes'] for interface in network_stats.values())
        return {'rx_bytes': rx_bytes, 'tx_bytes': tx_bytes}

    @staticmethod
    def calculate_block_io(stats):
        blkio_stats = stats['blkio_stats']['io_service_bytes_recursive']
        if not blkio_stats:
            return {'read_bytes': 0, 'write_bytes': 0}
        read_bytes = sum(entry['value'] for entry in blkio_stats if entry['op'] == 'Read')
        write_bytes = sum(entry['value'] for entry in blkio_stats if entry['op'] == 'Write')
        return {'read_bytes': read_bytes, 'write_bytes': write_bytes}

    def format_stats(self):

        self.containers.clear()
        for stats in self.containers_stats:
            self.containers.append(Container(
                container_id=stats['id'],
                name=stats['name'],
                cpu_percent=self.calculate_cpu_percent(stats),
                cpu_delta=self.get_cpu_delta(stats),
                system_cpu_delta=self.get_cpu_total(stats),
                number_cpus=self.get_num_cpus(stats),
                memory_utilization=self.calculate_memory_usage(stats),
                memory_total=stats['memory_stats']['limit'],
                network_in=self.calculate_network_io(stats)['rx_bytes'],
                network_out=self.calculate_network_io(stats)['tx_bytes'],
                block_in=self.calculate_block_io(stats)['read_bytes'],
                block_out=self.calculate_block_io(stats)['write_bytes'],
                raw_stats=stats
            ))

    def __repr__(self):
        return self.containers

    def to_dict(self):
        return [c.to_dict() for c in self.containers]


if __name__ == "__main__":
    usage = ContainerResourceUsage()
    usage.get_current_containers_stats()
    print(usage.to_dict())
