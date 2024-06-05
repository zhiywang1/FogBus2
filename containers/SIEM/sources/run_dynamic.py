import dotenv
import os
from utils.task_manager import TaskManager
from utils.task import Task
from utils.notifier import EmailNotifier
from utils.agent_talker import AgentTalker
from dynamic.policies.computation import ComputationPolicy
from dynamic.policies.network_host import NetworkHostPolicy
from dynamic.policies.network_container import NetworkContainerPolicy
from dynamic.policies.storage import StoragePolicy
from dynamic.policies.container import ContainerSuspiciousImagePolicy, ContainerSuspiciousSignaturePolicy


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


computation_policy = ComputationPolicy()


async def task_dynamic_computation():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_dynamic_computation()
        subject, body = computation_policy.apply(resp)
        if subject is None:
            continue
        body = format_body(agent_taker, body)
        email_notifier.send_email(subject, body)


network_host_policy = NetworkHostPolicy()


async def task_dynamic_network_host():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_dynamic_network_host()
        subject, body = network_host_policy.apply(resp)
        if subject is None:
            continue
        body = format_body(agent_taker, body)
        email_notifier.send_email(subject, body)


network_container_policy = NetworkContainerPolicy()


async def task_dynamic_network_container():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_dynamic_network_containers()
        subject, body = network_container_policy.apply(resp)
        if subject is None:
            continue
        body = format_body(agent_taker, body)
        email_notifier.send_email(subject, body)


storage_policy = StoragePolicy()


async def task_dynamic_storage():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_dynamic_storage()
        subject, body = storage_policy.apply(resp)
        if subject is None:
            continue
        body = format_body(agent_taker, body)
        email_notifier.send_email(subject, body)


container_image_policy = ContainerSuspiciousImagePolicy()


async def task_dynamic_container_image():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_dynamic_containers()
        subject, body, suspicious_containers = container_image_policy.apply(resp)
        if subject is None:
            continue
        for container in suspicious_containers:
            container_id = container['container_id']
            agent_taker.post_dynamic_stop_container(container_id)
        body = format_body(agent_taker, body)
        email_notifier.send_email(subject, body)


container_signature_policy = ContainerSuspiciousSignaturePolicy('master.crt')


async def task_dynamic_container_signature():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_dynamic_containers()
        subject, body, suspicious_containers = container_signature_policy.apply(resp)
        if subject is None:
            continue
        for container in suspicious_containers:
            container_id = container['container_id']
            agent_taker.post_dynamic_stop_container(container_id)
        body = format_body(agent_taker, body)
        email_notifier.send_email(subject, body)


if __name__ == "__main__":
    manager = TaskManager('SIME Dynamic')

    tasks = [
        # Task("Monitor Dynamic Computation Utilization", 5, task_dynamic_computation),
        # Task("Monitor Dynamic Network Host Utilization", 5, task_dynamic_network_host),
        # Task("Monitor Dynamic Network Container Utilization", 5, task_dynamic_network_container),
        # Task("Monitor Dynamic Storage Utilization", 5, task_dynamic_storage),
        # Task("Monitor Dynamic Container Image", 5, task_dynamic_container_image),
        Task("Monitor Dynamic Container Signature", 10000, task_dynamic_container_signature)
    ]

    for task in tasks:
        manager.add_task(task)

    manager.run()
