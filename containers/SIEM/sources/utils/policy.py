from abc import abstractmethod
from .notifier import EmailNotifier


class Policy:

    def __init__(self,
                 email_notifier: EmailNotifier):
        self.email_notifier = email_notifier

    @abstractmethod
    def apply(self,
              log):
        pass
