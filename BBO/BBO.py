import numpy as np

from changePath import changePath
from removeLoops import removeLoops
from pdist2 import pdist2
from calc_turns import calc_turns
from getPath import getPath
from plotPath3D import plotPath3D
import config_user as gl
from RouletteWheelSelection import RouletteWheelSelection

#####################################
# MAP creation#
sizeX, sizeY, sizeZ = 64, 64, 64
keys = []
for i in range(sizeX):
    for j in range(sizeY):
        for k in range(sizeZ):
            keys.append((i, j, k))
map_ = {key : 0 for key in keys}
#####################################
StartNode = (3, 3, 3)  # Start Node
GoalNode = (5, 6, 9)  # Goal Node

def run_bbo(StartNode, GoalNode):


    map_ = gl.map_
    sizeX, sizeY, sizeZ = gl.sizeX, gl.sizeY, gl.sizeZ


    # GSO Global Info
    class GlobalInfo:
        def __init__(self):
            # Initialize Global Best
            self.Cost = float('inf')
            self.Position = []
    GlobalBest = GlobalInfo()

    # GSO Class
    class Habitat:
        def __init__(self):
            # Create Empty Glowworm Structure
            self.Position = []
            self.NV = None
            self.Cost = None

    # Parameter Initialization
    nPop = 25
    MaxIt = 40
    nodes = 200

    # Constants for cost function
    k1, k2, k3 = 1, 80, 0.3

    KeepRate = 0.2 # Keep rate
    # nKeep = round(KeepRate * nPop)
    # I = 1 # max immigration rate for each island
    # E = 1 # max immigration rate, for each island

    mu = np.linspace(1, 0, nPop) # Emmigration Rates
    probs = []
    probDot = np.linspace(1, 0, nPop)
    pMutation = np.full((nPop),0.75)

    for j in range(nPop):
        probs.append(1./nPop)

    # CREATING Habitat
    habitats = []
    for i in range(nPop):
        habitats.append(Habitat())


    #BBO Algorithm Starts..........

    for i in range(0, nPop):
        path, CurrentNode, NVNodes = getPath(map_,StartNode, GoalNode, nodes, sizeX, sizeY,sizeZ)

        if CurrentNode == GoalNode or CurrentNode != GoalNode and NVNodes == (nodes + 1):
            habitats[i].Position = path
        elif NVNodes < nodes:
            continue
        else:
            habitats[i].Position = path

        habitats[i].NV = NVNodes

        turns = calc_turns(habitats[i].Position)
        habitats[i].Cost = k1 * len(path) + k2 * pdist2(CurrentNode, GoalNode) + k3 * turns

        if habitats[i].Cost < GlobalBest.Cost:
            GlobalBest.Cost = habitats[i].Cost
            GlobalBest.Position = habitats[i].Position

    # Algorithm initialization
    for it in range(0, MaxIt):

        maxCost = 0
        for i in range(0, nPop):
            if habitats[i].Cost > maxCost:
                maxCost = habitats[i].Cost

        for i in range(0, nPop):
            mu[i] = habitats[i].Cost/maxCost
        lambda_ = [x -1 for x in mu]

        for i in range(0, nPop):
            # Update path
            newPath = habitats[i].Position
            Cost = habitats[i].Cost

            if np.random.rand() <= lambda_:
                # Emmigration Probabilities
                EP = list(mu)
                EP[i] = 0
                EP = [x/sum(EP) for x in mu]

                # Select source Habitat
                j = RouletteWheelSelection(EP)
                mhabitat = habitats[i].Position
                toward = habitats[j].Position

                # Migration
                newPath, Cost = changePath(map_, mhabitat, toward, GoalNode, nodes)
                newPath = removeLoops(newPath)

            habitats[i].Position = newPath
            habitats[i].Cost = Cost

            if habitats[i].Cost < GlobalBest.Cost:
                GlobalBest.Cost = habitats[i].Cost
                GlobalBest.Position = habitats[i].Position

        # Calculation of mutation Probability
        maxCost = 0
        for i in range(0, nPop):
            if habitats[i].Cost > maxCost:
                maxCost = habitats[i].Cost

        for i in range(0, nPop):
            mu[i] = habitats[i].Cost/maxCost
        lambda_ = [x - 1 for x in mu]
####################
        if j < nPop:
            probPlus = probs[j+1]
            muPlus = mu[j+1]
        else:
            probPlus = 0
            muPlus = 0
        if i > 1:
            probMinus = probs[i - 1]
            lambdaMinus = lambda_[i-1]
        else:
            probMinus = 0
            lambdaMinus = 0
#######################

        probDot[i] = -(lambda_[i] + mu[i])* probs[i] + probMinus + muPlus * probPlus
        # probs = max(probs, 0)  ##############
        # probs =

        p = len(habitats[i].Position)
        temp1 = [1-x/p for x in probs]
        for i in range(nPop):
            pMutation[i] = pMutation[i] * temp1[i]


        for i in range(nPop):
            newPath = habitats[i].Position
            Cost = habitats[i].Cost

            # Mutation
            if np.random.rand() <= pMutation[j]:#######################
                newPath, Cost = changePath(map_, newPath, [], GoalNode, nodes)
                newPath = removeLoops(newPath)
            habitats[i].Position = newPath
            habitats[i].Cost = Cost

            if habitats[i].Cost < GlobalBest.Cost:
                GlobalBest.Cost = habitats[i].Cost
                GlobalBest.Position = habitats[i].Position

    print "Global Best Path:", GlobalBest.Position
    if GlobalBest.Position[-1] == GoalNode:
        print "Goal reached "
    else:
        print "Goal not reached"

    # Plot the path in 3D
    plotPath3D(GlobalBest.Position, GoalNode)

    return GlobalBest.Position

# path = run_bbo(StartNode,GoalNode)