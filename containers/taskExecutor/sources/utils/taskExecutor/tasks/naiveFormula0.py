from .base import BaseTask
from time import sleep
def starve(n):
    for i in range(n):
        i = i / 2

    
class NaiveFormula0(BaseTask):
    def __init__(self):
        super().__init__(taskID=108, taskName='NaiveFormula0')

    def exec(self, inputData):
        a = inputData['a']
        b = inputData['b']
        c = inputData['c']
        
        result = a + b + c
        inputData['resultPart0'] = result

        inputData['a'] += 1
        inputData['b'] += 1
        inputData['c'] += 1
        from random import randint
        for i in range(a):
            sleep(0.000000000001)
            starve(b + randint(1, 2))
        return inputData
