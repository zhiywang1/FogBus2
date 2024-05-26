import psutil
from ..common import ToDict


class DiskUsageInfo(ToDict):
    def __init__(self):
        self.disk_partitions = []
        self.disk_usage = {}

    def get_disk_partitions(self):
        self.disk_partitions = psutil.disk_partitions()

    def get_disk_usage(self):
        for partition in self.disk_partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                self.disk_usage[partition.device] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
            except PermissionError:
                self.disk_usage[partition.device] = {
                    'error': 'Permission denied'
                }


if __name__ == "__main__":
    disk_info = DiskUsageInfo()
    disk_info.get_disk_partitions()
    disk_info.get_disk_usage()
    print(disk_info)
