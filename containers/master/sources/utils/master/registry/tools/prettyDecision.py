from pprint import pformat

from ..registered.actors import RegisteredActors
from ...scheduler.types.decision import Decision


def prettyDecision(decision: Decision, registeredActor: RegisteredActors):
    inDict = {}
    taskNameList = decision.user.taskNameList
    indexToHostID = decision.indexToHostID
    for i, taskName in enumerate(taskNameList):
        actorHostID = indexToHostID[i]
        inDict[taskName] = registeredActor[actorHostID].nameLogPrinting
    return pformat(inDict, indent=8)
