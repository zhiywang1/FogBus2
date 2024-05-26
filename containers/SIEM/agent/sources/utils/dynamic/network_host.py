import subprocess
from pprint import pformat


class ToDict:

    def __repr__(self):
        return pformat(self.__dict__)

    def to_dict(self):
        return self.__dict__


class ConnectionInfo(ToDict):
    def __init__(self,
                 protocol,
                 local_address,
                 remote_address,
                 state,
                 pid_program):
        self.protocol = protocol
        self.local_address = local_address
        self.remote_address = remote_address
        self.state = state
        self.pid_program = pid_program


class SSUtilization:
    def __init__(self):
        self.connections = []

    def fetch_connections(self):
        result = subprocess.run(['ss', '-tupna'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error running ss command: {result.stderr}")
            return

        lines = result.stdout.splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                protocol = parts[0]
                local_address = parts[4]
                remote_address = parts[5]
                state = parts[1]
                pid_program = parts[6] if len(parts) > 6 else ''
                connection = ConnectionInfo(protocol, local_address, remote_address, state, pid_program)
                self.connections.append(connection)

    def to_dict(self):
        return [conn.to_dict() for conn in self.connections]


if __name__ == "__main__":
    ss_util = SSUtilization()
    ss_util.fetch_connections()
    connections = ss_util.to_dict()
    print(connections)
