import asyncio


class Task:
    def __init__(self,
                 name,
                 interval,
                 action):
        self.name = name
        self.interval = interval
        self.action = action
        self._task = None

    async def run(self):
        print(f'Task {self.name} starting')
        while True:
            await self.action()
            await asyncio.sleep(self.interval)

    def start(self):
        self._task = asyncio.create_task(self.run())

    def stop(self):
        if self._task:
            self._task.cancel()
