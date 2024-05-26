import os
import subprocess
from ..common import ToDict


class HostConfig(ToDict):
    def __init__(self):
        self.enabled_users = []
        self.ssh_users = []
        self.sudo_users = []
        self.logged_in_users = []
        self.logged_in_history = []

    def get_enabled_users(self):
        with open('/etc/passwd', 'r') as passwd_file:
            for line in passwd_file:
                parts = line.split(':')
                username, shell = parts[0], parts[-1].strip()
                if shell not in ['/usr/sbin/nologin', '/bin/false']:
                    self.enabled_users.append(username)

    def get_ssh_users(self):
        ssh_users = []
        with open('/etc/ssh/sshd_config', 'r') as sshd_config:
            for line in sshd_config:
                if line.strip().startswith('AllowUsers'):
                    ssh_users.extend(line.strip().split()[1:])
                elif line.strip().startswith('AllowGroups'):
                    allowed_groups = line.strip().split()[1:]
                    for group in allowed_groups:
                        group_users = subprocess.getoutput('getent group {}'.format(group)).split(':')[
                            -1].strip().split(',')
                        ssh_users.extend(group_users)

        if not ssh_users:
            with open('/etc/passwd', 'r') as passwd_file:
                for line in passwd_file:
                    parts = line.split(':')
                    username, shell = parts[0], parts[-1].strip()
                    if shell not in ['/usr/sbin/nologin', '/bin/false']:
                        ssh_users.append(username)

        self.ssh_users = ssh_users

    def get_sudo_users(self):
        sudoers_file = '/etc/sudoers'
        sudoers_dir = '/etc/sudoers.d'

        sudo_users = set()

        def parse_sudoers_file(filepath):
            with open(filepath, 'r') as file:
                for line in file:
                    if not line.startswith('#') and 'ALL' in line:
                        parts = line.split()
                        if parts and parts[0] != 'Defaults':
                            sudo_users.add(parts[0])

        parse_sudoers_file(sudoers_file)
        if os.path.isdir(sudoers_dir):
            for entry in os.listdir(sudoers_dir):
                filepath = os.path.join(sudoers_dir, entry)
                if os.path.isfile(filepath):
                    parse_sudoers_file(filepath)

        self.sudo_users = list(sudo_users)

    def get_logged_in_users(self):
        logged_in_users = []
        output = subprocess.getoutput('who')
        for line in output.splitlines():
            parts = line.split()
            if parts:
                logged_in_users.append(parts[0])
        self.logged_in_users = logged_in_users

    def get_logged_in_history(self):
        logged_in_history = []
        output = subprocess.getoutput('last')
        for line in output.splitlines():
            if line.startswith(('reboot', 'shutdown')):
                continue
            parts = line.split()
            if parts and len(parts) >= 5:
                user = parts[0]
                terminal = parts[1]
                hostname = parts[2]
                start_time = ' '.join(parts[3:7])
                if len(parts) >= 10:
                    end_time = ' '.join(parts[7:10])
                else:
                    end_time = 'still logged in'
                logged_in_history.append({
                    'user': user,
                    'terminal': terminal,
                    'hostname': hostname,
                    'start_time': start_time,
                    'end_time': end_time
                })
        self.logged_in_history = logged_in_history

if __name__ == "__main__":
    info = HostConfig()
    info.get_enabled_users()
    info.get_ssh_users()
    info.get_sudo_users()
    info.get_logged_in_users()
    print(info)
