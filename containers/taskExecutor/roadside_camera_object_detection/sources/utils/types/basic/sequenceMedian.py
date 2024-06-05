from threading import Lock
from typing import List


class SequenceMedian:

    def __init__(
            self,
            sequence: List[int] = None,
            maxRecordNumber: int = 100):
        self.__lock = Lock()
        self.maxRecordNumber = maxRecordNumber
        if sequence is None:
            self.index = 0
            self.sequence: List[int] = [0 for _ in
                                        range(self.maxRecordNumber)]
        else:
            self.index = len(sequence)
            self.sequence = sequence
        self._updated = False

    def update(self, value):
        self.__lock.acquire()
        self.sequence[self.index] = value
        self.index += 1
        if self.index >= self.maxRecordNumber:
            self.index = 0
        self._updated=True
        self.__lock.release()

    def median(self):
        index = self.index
        if self.index == 0:
            if self._updated:
                index = -1
            else:
                return self.sequence[0]
        # there is more efficient algorithm to find the median
        sequence = self.sequence[:index]
        sortedSequence = sorted(sequence)
        return sortedSequence[len(sortedSequence) >> 1]

    def __str__(self):
        return str(self.median())
