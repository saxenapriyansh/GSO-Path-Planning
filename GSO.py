import numpy as np

from changePath import changePath
from removeLoops import removeLoops
from pdist2 import pdist2
from calc_turns import calc_turns
from getPath import getPath
from plotPath3D import plotPath3D

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




# GSO Global Info
class GlobalInfo:
    def __init__(self):
        # Initialize Global Best
        self.Cost = float('inf')
        self.Position = []
GlobalBest = GlobalInfo()

# GSO Class
class Glowworm:
    def __init__(self):
        # Create Empty Glowworm Structure
        self.Position = []
        self.range = None
        self.luciferin = None
        self.NV = None
        self.Cost = None


StartNode = (3,3,3) #Start Node
GoalNode = (5,6,4) #Goal Node



# Parameter Initialization
nPop = 50
MaxIt = 40
nodes = 50

# RANGE
range_init = 5.0
range_boundary = 50.2

# LUCIFERIN
luciferin_init = 25
luciferin_decay = 0.4
luciferin_enhancement = 0.6

# Neighbors
k_neigh = 20
beta = 0.5

# Constants for cost function
k1, k2, k3 = 1, 80, 0.3

# CREATING GLOWWORMS
glowworms = []
for i in range(nPop):
    glowworms.append(Glowworm())


#GSO Algorithm Starts..........

for i in range(0,nPop):
    path, CurrentNode, NVNodes = getPath(map_,StartNode, GoalNode, nodes, sizeX, sizeY,sizeZ)
    if CurrentNode == GoalNode or CurrentNode != GoalNode and NVNodes == (nodes + 1):
        glowworms[i].Position = path
    elif NVNodes < nodes:
        continue
    else:
        glowworms[i].Position = path

    glowworms[i].range = range_init
    glowworms[i].NV = NVNodes
    glowworms[i].luciferin = luciferin_init

    turns = calc_turns(glowworms[i].Position)
    glowworms[i].Cost = k1 * len(path) + k2 * pdist2(CurrentNode, GoalNode) + k3 * turns
    if glowworms[i].Cost < GlobalBest.Cost:
        GlobalBest.Cost = glowworms[i].Cost
        GlobalBest.Position = glowworms[i].Position

# Algorithm initialization
for it in range(0,MaxIt):
    for i in range(0, nPop):
        if i==2:
            pass

        # Update luciferin
        glowworms[i].luciferin = (1-luciferin_decay) * glowworms[i].luciferin + luciferin_enhancement * (glowworms[i].Cost/10)
        neighbors = []

        for k in range(0,nPop):
            dist = abs(glowworms[i].Cost - glowworms[k].Cost)
            if dist != 0 and dist <= glowworms[i].range and glowworms[i].luciferin < glowworms[k].luciferin:
                neighbors.append(k)

        if len(neighbors) > 0:
            li = glowworms[i].luciferin

            sum_lk = 0
            for worm_idx in neighbors:
                sum_lk = sum_lk + glowworms[worm_idx].luciferin


            #Calc probabilities for each neighbour to be followed
            probs_numerator = []
            for worm_index in neighbors:
                probs_numerator.append(abs(glowworms[worm_index].luciferin - glowworms[i].luciferin))

            probs = []
            for i in range(len(probs_numerator)):
                probs.append(probs_numerator[i]/(sum_lk - (len(probs_numerator)*li)))

            #Calc prob range
            acc = 0
            wheel = []
            for prob in probs:
                acc += prob
                wheel.append(acc)

            wheel[-1] = 1

            #randomly choose a value for wheel selection method
            rand_val = np.random.random()
            following = 0
            for idx, value in enumerate(wheel):
                if rand_val <= value:
                    following = idx
            #         add break if necessary

            toward_index = neighbors[following]

            # Position update
            glowworm = glowworms[i].Position
            toward = glowworms[toward_index].Position

            newPath, Cost = changePath(map_, glowworm, toward, GoalNode, nodes)
            newPath = removeLoops(newPath)

            glowworms[i].Position = newPath
            glowworms[i].Cost = Cost

        elif len(neighbors) == 0:
            glowworm = glowworms[i].Position
            newPath, Cost = changePath(map_, glowworm, [], GoalNode, nodes)
            newPath = removeLoops(newPath)

            glowworms[i].Position = newPath
            glowworms[i].Cost = Cost

        # Updating range
        glowworms[i].range = min(range_boundary, max(0.1, glowworms[i].range + beta*(k_neigh - len(neighbors))))

        if glowworms[i].Cost < GlobalBest.Cost:
            GlobalBest.Cost = glowworms[i].Cost
            GlobalBest.Position = glowworms[i].Position


print "Global Best Path:", GlobalBest.Position
if GlobalBest.Position[-1] == GoalNode:
    print "Goal reached "
else:
    print "Goal not reached"

# Plot the path in 3D
plotPath3D(GlobalBest.Position, GoalNode)



