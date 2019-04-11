import numpy as np
from math import floor
import random

from changePath import changePath
from removeLoops import removeLoops
from pdist2 import pdist2
from calc_turns import calc_turns
from getPath import getPath
from plotPath3D import plotPath3D
import config_user as gl


#####################################
# MAP creation#
sizeX, sizeY, sizeZ = 20, 20, 20
keys = []
for i in range(sizeX):
    for j in range(sizeY):
        for k in range(sizeZ):
            keys.append((i, j, k))
map_ = {key : 0 for key in keys}
#####################################



def sortFunction(ob):
    return ob.Cost

def run_iwo(StartNode, GoalNode):




    # IWO Global Info
    class GlobalInfo:
        def __init__(self):
            # Initialize Global Best
            self.Cost = float('inf')
            self.Position = []
    GlobalBest = GlobalInfo()

    # IWO Class
    class Weed:
        def __init__(self):
            # Create Empty Glowworm Structure
            self.Position = []
            self.Cost = float('inf')

    # Problem Definition
    nVar = 5
    # VarSize = [1 nVar]
    VarMin = -10
    VarMax = 10

    # IWO Parameters

    MaxIt = 20

    nPop0 = 10
    nPop = 25

    Smin = 0
    Smax = 5

    Exponent = 3
    sigma_initial = 0.5
    sigma_final = 0.001

    # Constants for cost function
    k1, k2, k3 = 1, 80, 0.3

    # CREATING GLOWWORMS
    weeds = []
    for i in range(nPop):
        weeds.append(Weed())

    nodes = 200
    #IWO Algorithm Starts..........
    for i in range(0,nPop):
        path, CurrentNode, NVNodes = getPath(map_,StartNode, GoalNode, nodes, sizeX, sizeY,sizeZ)

        if CurrentNode == GoalNode or CurrentNode != GoalNode and NVNodes == (nodes + 1):
            weeds[i].Position = path
        elif NVNodes < nodes:
            continue
        else:
            weeds[i].Position = path

        turns = calc_turns(weeds[i].Position)
        weeds[i].Cost = k1 * len(path) + k2 * pdist2(CurrentNode, GoalNode) + k3 * turns

        if weeds[i].Cost < GlobalBest.Cost:
            GlobalBest.Cost = weeds[i].Cost
            GlobalBest.Position = weeds[i].Position

    # Algorithm initialization

    for it in range(MaxIt):

        if GlobalBest.Position[-1] == GoalNode:
            break

        sigma = ((MaxIt - it) / (MaxIt - 1)) ** Exponent * (sigma_initial - sigma_final) + sigma_final

        WorstCost, BestCost = 0, float('inf')
        for weed in weeds:
            if weed.Cost < BestCost:
                BestCost = weed.Cost    # min Cost
            if weed.Cost > WorstCost:
                WorstCost = weed.Cost  # max Cost

        # # New Weeds produced
        # newWeeds = []
        # for i in range(nPop):
        #     newWeeds.append(Weed())


        # Reproduction
        newWeeds = []
        for i in range(0, nPop):
            # Generate Seeds
            if BestCost - WorstCost != 0:
                ratio = (weeds[i].Cost - WorstCost) / (BestCost - WorstCost)
            else:
                ratio = random.uniform(0, 1)

            
            S = int(floor(Smin + (Smax - Smin) * ratio))

            for seed in range(S):
                # Initialize Offsprings
                newWeedInstance = Weed()

                newPath, Cost = changePath(map_, weeds[i].Position, [], GoalNode, nodes)
                newPath = removeLoops(newPath)

                newWeedInstance.Position = newPath
                newWeedInstance.Cost = Cost

                # newWeeds.extend(newWeeds)
                newWeeds.append(newWeedInstance)

        # Merge population
        weeds.extend(newWeeds) # Check

        # Sort Population
        weeds.sort(key= sortFunction, reverse=False)

        # Competitive Exclusion(Delete Extra Members)
        if len(weeds) > nPop:
            weeds[nPop:] = ()

        # Store Path iff goal is reached and cost is less
        for i in range(nPop):
            if weeds[i].Cost < GlobalBest.Cost and weeds[i].Position[-1] == GoalNode:
                GlobalBest.Cost = weeds[i].Cost
                GlobalBest.Position = weeds[i].Position
                break

    print "Global Best Path:", GlobalBest.Position
    if GlobalBest.Position[-1] == GoalNode:
        print "Goal", GoalNode, "reached"
    else:
        print "Goal:", GoalNode," not reached"

    # Plot the path in 3D
    # plotPath3D(GlobalBest.Position, GoalNode)

    return GlobalBest.Position

# run_iwo((0,0,0),(0,0,0))
