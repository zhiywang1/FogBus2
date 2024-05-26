class StoragePolicy:

    def __init__(self):
        self.threshold = 50

    def apply(self,
              data):
        disk_util = data['data']['disk_usage']

        not_satisfied = []
        for device, utilization in disk_util.items():
            if utilization['percent'] > self.threshold:
                not_satisfied.append(device)
        if len(not_satisfied):
            body = '\r\n'.join(not_satisfied)
            return f'[WARNING] Storage Usage Exceeded {self.threshold}%', body
        return None, None
