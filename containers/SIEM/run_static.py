import dotenv
import os
from utils.task_manager import TaskManager
from utils.task import Task
from utils.notifier import EmailNotifier
from utils.agent_talker import AgentTalker
from static.policies.images import ImagesPolicy


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

images_policy = ImagesPolicy(email_notifier=email_notifier)


async def task_static_images():
    for agent_taker in agent_talkers:
        resp = agent_taker.get_static_images()
        subject, body = images_policy.apply(resp)
        if subject is None:
            continue
        body = (f'IP: {agent_taker.ip}\r\n'
                f'Port: {agent_taker.port}\r\n'
                f'API: {agent_taker.base_url}\r\n'
                f'\r\n{body}')
        email_notifier.send_email(subject, body)


if __name__ == "__main__":
    manager = TaskManager('SIME Static')

    task1 = Task("Task1", 5, task_static_images)

    manager.add_task(task1)

    manager.run()
