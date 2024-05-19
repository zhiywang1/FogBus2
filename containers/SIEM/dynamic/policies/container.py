class ContainerPolicy:

    def __init__(self):
        self.valid_images = set(self.get_valid_images())

    @staticmethod
    def get_valid_images():
        with open('valid_images.list', 'r') as f:
            return [line.strip() for line in f.readlines()]

    def apply(self,
              data):
        containers = data['data']
        suspicious_containers = []
        for container in containers:
            image_id = container['image_id']
            if image_id not in self.valid_images:
                suspicious_containers.append(container)
        if len(suspicious_containers):
            body = '\r\n'.join([str(container) for container in suspicious_containers])
            return '[WARNING] Suspicious Container with Unrecognized Image', body, suspicious_containers
        return None, None, None
