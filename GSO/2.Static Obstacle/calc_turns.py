import numpy as np

def calc_turns(path):
    turns = 0
    lim = len(path)
    for i in range(1, lim-1):
        if np.array_equal(np.subtract(path[i], path[i-1]), np.subtract(path[i+1], path[i])):
            turns = turns + 1
    return turns