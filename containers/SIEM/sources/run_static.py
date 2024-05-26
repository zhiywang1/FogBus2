import dotenv
import os
from utils.task_manager import TaskManager
from utils.task import Task
from utils.notifier import EmailNotifier
from utils.agent_talker import AgentTalker
from static.policies.images import ImagesPolicy
from static.policies.storage import StoragePolicy
from static.policies.network import NetworkPolicy
from static.policies.host_config import HostConfigPolicy


def load_hosts():
    with open("hosts.list") as f:
        _hosts = f.readlines()
        _hosts = [x.strip() for x in _hosts]
        return _hosts


hosts = load_hosts()
dotenv.load_dotenv()
email_username = os.getenv("GMAIL_USER")
email_password = os.getenv("GMAIL_APP_PASS")
email_notifier = EmailNotifier(
    username=email_username,
    password=email_password)

http_basic_auth_user = os.getenv("AGENT_BASIC_HTTP_USER")
http_basic_auth_pass = os.getenv("AGENT_BASIC_HTTP_PASS")

agent_talkers = []
for host in hosts:
    hostname, port = host.split(":")
    port = int(port)
    agent_talkers.append(AgentTalker(
        hostname, port, http_basic_auth_user, http_basic_auth_pass))


def format_body(agent_taker,
                body):
    return (f'IP: {agent_taker.ip}\r\n'
            f'Port: {agent_taker.port}\r\n'
            f'API: {agent_taker.base_url}\r\n'
            f'\r\n{body}')


images_policy = ImagesPolicy()


async def task_static_images():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_static_images()
        subject, body = images_policy.apply(resp)
        if subject is None:
            continue
        body = format_body(agent_taker, body)
        email_notifier.send_email(subject, body)


storage_policy = StoragePolicy()


async def task_static_storage():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_static_storage()
        subject, body = storage_policy.apply(resp)
        if subject is None:
            continue
        body = format_body(agent_taker, body)
        email_notifier.send_email(subject, body)


network_policy = NetworkPolicy()


async def task_static_network():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_static_network_config()
        subject, body = network_policy.apply(resp)
        if subject is None:
            continue
        body = format_body(agent_taker, body)
        email_notifier.send_email(subject, body)


host_config_policy = HostConfigPolicy()


async def task_static_host_config():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_static_host_config()
        subject, body = host_config_policy.apply(resp)
        if subject is None:
            continue
        body = format_body(agent_taker, body)
        email_notifier.send_email(subject, body)


if __name__ == "__main__":
    manager = TaskManager('SIME Static')

    tasks = [
        Task("Scan Images", 600, task_static_images),
        Task("Scan Storage", 600, task_static_storage),
        Task("Scan Host Network Config", 600, task_static_network),
        Task("Scan Host Config", 600, task_static_host_config)
    ]

    for task in tasks:
        manager.add_task(task)

    manager.run()
