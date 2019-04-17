def collisionTest(map_, CurrentNeighbours):
    sDel = []
    for idx, node in enumerate(CurrentNeighbours):
        if map_[node] == -1 or map_[node] == -2:
            sDel.append(idx)
    if sDel:
        sDel = set(sDel)
        for i in sorted(sDel, reverse=True):
            del CurrentNeighbours[i]
    return CurrentNeighbours