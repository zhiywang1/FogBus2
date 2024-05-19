class StoragePolicy:

    @staticmethod
    def apply(data):
        disk_util = data['data']['disk_usage']

        threshold = 5
        not_satisfied = []
        for device, utilization in disk_util.items():
            if utilization['percent'] > threshold:
                not_satisfied.append(device)
        if len(not_satisfied):
            body = '\r\n'.join(not_satisfied)
            return f'[WARNING] Storage Usage Exceeded {threshold}%', body
        return None, None
