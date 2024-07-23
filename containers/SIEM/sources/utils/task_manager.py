import asyncio


class TaskManager:
    def __init__(self,
                 name):
        self.name = name
        self.tasks = []

    def add_task(self,
                 task):
        self.tasks.append(task)

    async def start(self):
        for task in self.tasks:
            task.start()
        print(f'[*] TaskManager {self.name} is running: {len(self.tasks)} tasks')
        while True:
            await asyncio.sleep(1)

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            pass
        finally:
            for task in self.tasks:
                task.stop()
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
