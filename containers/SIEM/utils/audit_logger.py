from abc import abstractmethod


class AuditLogger:
    def __init__(self):
        pass

    @abstractmethod
    def log(self,
            message):
        pass


class FileAuditLogger(AuditLogger):
    def __init__(self,
                 file_path):
        super().__init__()
        self.file_path = file_path

    def log(self,
            message):
        with open(self.file_path, 'a') as file:
            file.write(message + '\n')
