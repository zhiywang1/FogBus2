class StoragePolicy:

    def __init__(self):
        self.threshold_read_bytes = 0
        self.threshold_write_bytes = 0

    def apply(self,
              data):
        data = data['data']
        suspicious_containers = []
        for container in data:
            read_bytes = container['read_bytes']
            write_bytes = container['write_bytes']
            if read_bytes > self.threshold_read_bytes or write_bytes > self.threshold_write_bytes:
                suspicious_containers.append(str(container))
                break
        if len(suspicious_containers):
            body = '\r\n'.join(suspicious_containers)
            return f'[WARNING] Found Suspicious Container Storage Utilization', body
        return None, None
