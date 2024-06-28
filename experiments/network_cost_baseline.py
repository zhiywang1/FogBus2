import subprocess
import mysql.connector
from time import sleep, time
from tqdm import tqdm

def run_ssh_command(host, command):
    process = subprocess.Popen(["ssh", host, f"``{command}``"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print(f'[*] Running command: ssh {host} {command}')
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8'), stderr.decode('utf-8')


class Base:
    def __init__(self, host, start_command, stop_command, name):
        self.host = host
        self._start_command = start_command
        self._stop_command = stop_command
        self.name = name

    def start(self):
        print(f'[*] Start {self.name} on {self.host}')
        out, err = run_ssh_command(self.host, self._start_command)

    def stop(self):
        print(f'[*] Stop {self.name} on {self.host}')
        out, err = run_ssh_command(self.host, self._stop_command)
        if err:
            print(f'[!] Error: {err}')
            self.stop_all()

    def stop_all(self):
        run_ssh_command(self.host, 'docker stop $(docker ps -a -q)')




def get_delay_info(cursor):
    sql = 'SELECT * FROM delay'
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows


def parse_delays(rows, delays):
    for row in rows:
        source, dest, delay, _ = row
        if source not in delays:
            delays[source] = {}
        if dest not in delays[source]:
            delays[source][dest] = []
        delays[source][dest].append(delay)


def save_delays(delays, filename):
    with open(filename, 'w') as f:
        for k, v in delays.items():
            for k2, v2 in v.items():
                for v3 in v2:
                    f.write(f'{k},{k2},{v3}\r\n')
        f.close()
        print(f'[+] Delays saved to {filename}')


def truncate_table(cursor):
    sql = 'TRUNCATE TABLE delay'
    cursor.execute(sql)
    conn.commit()


if __name__ == "__main__":
    delays = {}
    # for i in range(2):
    #     rows = get_delay_info()
    #     parse_delays(rows, delays)
    # print(delays)
    # save_delays(delays, 'delays.csv')
    # exit()
    # start mariadb
    db = Base('aws', 'docker start fogbus2-mariadb', 'docker stop fogbus2-mariadb', 'fogbus2-mariadb')
    db.stop_all()
    db.start()
    sleep(3)
    conn = mysql.connector.connect(
        host="100.96.133.1",
        port="3306",
        user="root",
        password="passwordForRoot",
        database="fogbus2_systemperformance")
    cursor = conn.cursor()

    truncate_table(cursor)
    # start remote logger
    remote_logger = Base('aws',
                         'cd ~/FogBus2/containers/remoteLogger && '
                         'docker compose run --rm -d '
                         '--name RemoteLogger fogbus2-remote_logger '
                         '--bindIP 100.96.133.1 '
                         '--bindPort 5000 '
                         '--containerName RemoteLogger',
                         'docker rm -f $(docker ps | grep RemoteLogger | cut -c 1-10)', 'RemoteLogger')

    remote_logger.start()
    sleep(2)

    # start master
    master = Base('rpi-a',
                  'cd ~/FogBus2/containers/master && '
                  'docker compose run --rm -d '
                  '--name Master fogbus2-master '
                  '--bindIP 100.65.189.23 '
                  '--bindPort 5001 '
                  '--remoteLoggerIP 100.96.133.1 '
                  '--remoteLoggerPort 5000 '
                  '--containerName Master',
                  'docker rm -f $(docker ps | grep Master | cut -c 1-10)', 'Master')
    master.stop_all()
    master.start()
    sleep(40)

    # start actor

    actor = Base('nectar-k8s32vcpu30gb',
                 'cd ~/FogBus2.0.1/containers/actor && '
                 'docker compose run --rm -d --name Actor fogbus2-actor '
                 '--masterIP 100.65.189.23 '
                 '--masterPort 5001 '
                 '--remoteLoggerIP 100.96.133.1 '
                 '--remoteLoggerPort 5000 '
                 '--bindIP 100.106.159.123 '
                 '--containerName Actor',
                 'docker rm -f $(docker ps | grep Actor | cut -c 1-10)', 'Actor')
    actor.stop_all()
    actor.start()
    sleep(5)

    # start user
    for i in tqdm(range(1)):
        user = Base('rpi-d',
                    'cd ~/FogBus2/containers/user && '
                    'docker compose run --rm -d --name User fogbus2-user '
                    '--bindIP 100.65.86.34 '
                    '--bindPort 50200 '
                    '--masterIP 100.65.189.23 '
                    '--masterPort 5001 '
                    '--remoteLoggerIP 100.96.133.1 '
                    '--remoteLoggerPort 5000 '
                    '--applicationName NaiveFormulaSerialized',
                    'docker stop $(docker ps | grep User | cut -c 1-10)', 'User')
        user.stop_all()
        user.start()
    #     sleep(30)
    #     user.stop()
    #     # run_ssh_command('nectar-k8s32vcpu30gb', 'docker rm -f $(docker ps | grep Naive | cut -c 1-10)')
    #     rows = get_delay_info(cursor)
    #     parse_delays(rows, delays)
    #     save_delays(delays, f'delays-baseline-{time()}.csv')
    # actor.stop()
    # master.stop()
    # remote_logger.stop()
    # db.stop()
