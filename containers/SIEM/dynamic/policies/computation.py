class ComputationPolicy:

    def __init__(self):
        self.memory_threshold = 80
        self.cpu_threshold = 80

    def apply(self,
              data):
        data = data['data']
        suspicious_containers = []
        for container_data in data:
            cpu_percent = container_data['cpu_percent'] * 100
            memory_percent = container_data['memory_utilization']['percent'] * 100
            if cpu_percent > self.cpu_threshold or memory_percent > self.memory_threshold:
                container_id = container_data['id']
                suspicious_containers.append(f'{container_id}, {cpu_percent}, {memory_percent}')

        if len(suspicious_containers):
            body = '\r\n'.join(suspicious_containers)
            return f'[WARNING] CPU ({self.cpu_threshold}%) or Memory ({self.memory_threshold}%) Usage Exceeded', body
        return None, None
