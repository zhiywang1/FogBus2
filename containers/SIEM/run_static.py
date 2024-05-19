from utils.task_manager import TaskManager
from utils.task import Task


async def sample_task_action():
    print("Task executed")


if __name__ == "__main__":
    manager = TaskManager('SIME Static')

    task1 = Task("Task1", 2, sample_task_action)
    task2 = Task("Task2", 3, sample_task_action)

    manager.add_task(task1)
    manager.add_task(task2)

    manager.run()
