import os.path
from abc import abstractmethod
from time import time


class AuditLogger:
    def __init__(self):
        pass

    @abstractmethod
    def log(self,
            message,
            *arg,
            **kwargs):
        pass


class FileAuditLogger(AuditLogger):
    def __init__(self,
                 folder_path):
        super().__init__()
        self.folder = folder_path

    def log(self,
            message,
            *arg,
            **kwargs):
        path = os.path.join(self.folder, f"{kwargs['file_path']}.log")
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        message = f"{time()} - {message}"
        with open(path, 'a+') as file:
            file.write(message + '\n')
