class NetworkContainerPolicy:

    def __init__(self):
        self.threshold_rx_bytes = 1000000
        self.threshold_tx_bytes = 1000000

    def apply(self,
              data):
        data = data['data']
        suspicious_containers = []
        for container in data:
            network_usages = container['network_usage']
            for network_usage in network_usages:
                rx_bytes = network_usage['rx_bytes']
                tx_bytes = network_usage['tx_bytes']
                if rx_bytes > self.threshold_rx_bytes or tx_bytes > self.threshold_tx_bytes:
                    suspicious_containers.append(str(container))
                    break
        if len(suspicious_containers):
            body = '\r\n'.join(suspicious_containers)
            return f'[WARNING] Found Suspicious Container Network Utilization', body
        return None, None
