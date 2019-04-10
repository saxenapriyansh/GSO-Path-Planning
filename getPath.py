from math import ceil
import numpy as np

from neighbours import neighbours
from collisionTest import collisionTest

def getPath(map_, StartNode, GoalNode, nodes, sizeX, sizeY,sizeZ):
    NodesEvaluated={StartNode:1}
    CurrentNode = StartNode
    paths = [StartNode]
    curNodeIndex = 1
    NVNodes = 0
    prevNode = GoalNode

    while NVNodes < nodes and CurrentNode != GoalNode:
        hor = 1 if CurrentNode[0] > GoalNode[0] else 0
        ver = 1 if CurrentNode[1] > GoalNode[1] else 0
        plan = 1 if CurrentNode[2] > GoalNode[2] else 0

        if CurrentNode[0] == GoalNode[0]:
            hor = 2
        if CurrentNode[1] == GoalNode[1]:
            ver = 2
        if CurrentNode[2] == GoalNode[2]:
            plan = 2

        directions = (ver,hor,plan)
        CurrentNeighbours, ViableNeighbours = neighbours(CurrentNode, directions, sizeX, sizeY,sizeZ)
        CurrentNeighbours = collisionTest(map_, CurrentNeighbours)
        ViableNeighbours = collisionTest(map_, ViableNeighbours)

        CurrentNeighboursABS = []
        for key in CurrentNeighbours:
            if key not in NodesEvaluated:
                CurrentNeighboursABS.append(key)

        temp = []
        for i in ViableNeighbours:
            if i in prevNode:
                temp.append(i)
        ViableNeighbours = temp

        ViableNeighboursABS = []
        for key in ViableNeighbours:
            if key not in NodesEvaluated:
                ViableNeighboursABS.append(key)
        flag = 0
        if ViableNeighboursABS:
            pos = int(max(0, ceil(np.random.random() * len(ViableNeighboursABS))-1))
            pos = ViableNeighboursABS[pos]
        elif not ViableNeighboursABS and CurrentNeighboursABS:
            pos = int(max(0, ceil(np.random.random() * len(CurrentNeighboursABS))-1))
            pos = CurrentNeighboursABS[pos]
            flag = 1
        elif not CurrentNeighboursABS and ViableNeighbours:
            pos = int(max(0, ceil(np.random.random() * len(ViableNeighbours))-1))
            pos = ViableNeighbours[pos]
        elif not ViableNeighbours and CurrentNeighbours:
            pos = int(max(0, ceil(np.random.random() * len(CurrentNeighbours))-1))
            pos = CurrentNeighbours[pos]
            flag = 1
        else:
            break


        if flag == 1:
            NVNodes = NVNodes +1
        paths.append(pos)
        NodesEvaluated[pos] = 1
        prevNode = CurrentNode
        CurrentNode = pos
        curNodeIndex = curNodeIndex + 1

    return paths, CurrentNode, NVNodes