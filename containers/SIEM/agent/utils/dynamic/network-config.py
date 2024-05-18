import psutil
from pprint import pformat
from psutil import CONN_LISTEN


class Address:
    def __init__(self, addr):
        if len(addr) == 0:
            self.ip = None
            self.port = None
        else:
            self.ip = addr[0]
            self.port = addr[1]

    def __repr__(self):
        return pformat(self.__dict__)


class Connection:
    def __init__(self, local_addr, remote_addr, status, pid):
        self.local_addr: Address = local_addr
        self.remote_addr: Address = remote_addr
        self.status = status
        self.pid = pid

    def __repr__(self):
        return pformat(self.__dict__)


class NetworkConfigScanner:
    def __init__(self):
        self.connections: list[Connection] = []

    def collect(self):
        self.connections.clear()
        connections = psutil.net_connections()
        for conn in connections:
            self.connections.append(
                Connection(
                    Address(conn.laddr),
                    Address(conn.raddr),
                    conn.status,
                    conn.pid
                )
            )

    def get_current_connections(self):
        self.collect()
        return self.connections

    def filter_open_connections(self):
        connections = []
        for conn in self.connections:
            if conn.status == CONN_LISTEN:
                connections.append(conn)
        return connections

    def __repr__(self):
        return pformat(self.connections)


# Example usage
if __name__ == "__main__":
    scanner = NetworkConfigScanner()
    scanner.get_current_connections()
    print(scanner)
