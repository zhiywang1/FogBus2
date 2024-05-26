class NetworkHostPolicy:

    def __init__(self):
        self.blacklist = {'0.0.0.0:8080'}

    def apply(self,
              data):
        data = data['data']
        suspicious_connections = []
        for conn in data:
            local_address = conn['local_address']
            if local_address in self.blacklist:
                suspicious_connections.append(str(conn))
        if len(suspicious_connections):
            body = '\r\n'.join(suspicious_connections)
            return f'[WARNING] Found Suspicious Connections', body
        return None, None
