import numpy as np
import math
from numpy import random

from getPath import getPath
from removeLoops import removeLoops
from pdist2 import pdist2
from calc_turns import calc_turns
import config_user as gl




def changePath(map_, weakSol, strongSol, GoalNode, nodes):
    k1 = 1
    k2 = 80
    k3 = 0.3


    if strongSol:
        C = [value for value in weakSol if value in strongSol]
        if C:
            pos = C[0]
            weakPos = weakSol.index(pos)
            strongPos = strongSol.index(pos)
            weakSol = weakSol[:weakPos]
            weakSol.extend((strongSol[strongPos],))
            newpath = weakSol
            newpath = removeLoops(newpath)
            turns = calc_turns(newpath)
            Cost = k1 * len(newpath) + k2 * pdist2(newpath[-1], GoalNode) + k3 * turns

        else:
            spath1 = len(weakSol)
            spath2 = len(strongSol)
            random_t = random.random()
            pos1 = int(math.floor(random_t * spath1))

            newpath = weakSol[0:pos1]
            wNode = weakSol[pos1]
            cNode = wNode
            sNode = GoalNode
            Mcounter = 100
            counter = 0
            tpath = []

            while cNode != sNode and counter <= Mcounter:
                pos2 = int(math.floor(random.random() * spath2))
                sNode = strongSol[pos2]
                tpath, cNode, _ = getPath(map_, wNode, sNode, math.ceil(nodes / 2), gl.sizeX, gl.sizeY, gl.sizeZ)
                counter = counter + 1

            if counter <= Mcounter:
                newpath.extend(tpath[1:])
                tpath, _, _ = getPath(map_, sNode, GoalNode, math.ceil(nodes / 2), gl.sizeX, gl.sizeY, gl.sizeZ)
                newpath.extend(tpath[1:])
            else:
                newpath = weakSol

            newpath = removeLoops(newpath)
            turns = calc_turns(newpath)
            Cost = k1 * len(newpath) + k2 * pdist2(newpath[-1], GoalNode) +k3 * turns


    else:
        Mcounter = 100
        counter = 0
        spath1 = len(weakSol)
        pos1 = int(math.floor(random.random() * spath1))
        newpath = weakSol[0:pos1]
        tpath = []

        wNode = weakSol[pos1]
        cNode = wNode
        sNode = GoalNode

        while cNode != sNode and counter <= Mcounter:
            sNode = (int(np.random.random() * gl.sizeX), int(np.random.random() * gl.sizeY), int(np.random.random() * gl.sizeZ))
            tpath, cNode, _ = getPath(map_, wNode, sNode, math.ceil(nodes / 2), gl.sizeX, gl.sizeY, gl.sizeZ)
            counter = counter + 1

        if counter <= Mcounter and tpath:
            newpath.extend(tpath[1:])
            tpath, _, _ = getPath(map_, sNode, GoalNode, math.ceil(nodes / 2), gl.sizeX, gl.sizeY, gl.sizeZ)
            newpath.extend(tpath[1:])
        else:
            newpath = weakSol

        newpath = removeLoops(newpath)
        turns = calc_turns(newpath)
        Cost = k1 * len(newpath) + k2 * pdist2(newpath[-1], GoalNode) + k3 * turns

    return newpath, Cost
