def succ6(s, sizeX, sizeY, sizeZ):
    """
    Find which nodes can be moved to next from node s, excluding diagonals
    Used to mark nodes within safety margin since its faster than using all 26 successors
    """
    x, y, z = s

    # Define successor states, one down in z-direction
    sDel = []
    succNode = [
        (x + 1, y, z),  # Keep - 11   2
        (x - 1, y, z),  # Keep - 15   4

        (x, y + 1, z),  # Keep - 9    1
        (x, y - 1, z),  # Keep - 13   3

        (x,   y,   z+1),  # Keep - 8    0
        (x,   y,   z-1),  # Keep - 25  5
    ]

    # Nodes to delete when on a boundary
    if x == sizeX-1:
        sDel.append(0)
    elif x == 0:
        sDel.append(1)

    if y == sizeY-1:
        sDel.append(2)
    elif y == 0:
        sDel.append(3)

    if z == sizeZ-1:
        sDel.append(4)
    elif z == 0:
        sDel.append(5)

    if sDel:
        sDel = set(sDel)
        for i in sorted(sDel, reverse=True):
            del succNode[i]

    return succNode



def neighbours(CurrentNode, directions, sizeX, sizeY, sizeZ):
    x, y, z = CurrentNode
    if not CurrentNode:
        return [], []

    CurrentNeighbours = succ6(CurrentNode, sizeX, sizeY, sizeZ)
    ViableNeighbours = []

    if directions[0] == 0 and x+1 < sizeX:
        ViableNeighbours.append((x + 1, y, z))
    elif directions[0] == 1 and x-1 >= 0:
        ViableNeighbours.append((x - 1, y, z))

    if directions[1] == 0 and y+1 < sizeY:
        ViableNeighbours.append((x, y+1, z))
    elif directions[1] == 1 and y-1 >= 0:
        ViableNeighbours.append((x, y-1, z))

    if directions[2] == 0 and z+1 < sizeZ:
        ViableNeighbours.append((x, y, z+1))
    elif directions[2] == 1 and z-1 >= 0:
        ViableNeighbours.append((x, y, z-1))

    temp = []
    for x in ViableNeighbours:
        if x is not None:
            temp.append(x)
    ViableNeighbours = temp

    return CurrentNeighbours, ViableNeighbours