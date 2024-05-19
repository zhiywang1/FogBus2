import dotenv
import os
from utils.task_manager import TaskManager
from utils.task import Task
from utils.notifier import EmailNotifier


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


async def sample_task_action():
    print("Task executed")


if __name__ == "__main__":
    manager = TaskManager('SIME Static')

    task1 = Task("Task1", 5, sample_task_action)
    task2 = Task("Task2", 5, sample_task_action)

    manager.add_task(task1)
    manager.add_task(task2)

    manager.run()
