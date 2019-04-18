from math import sqrt

def pdist2(us, ut):
    x1, y1, z1 = us
    x2, y2, z2 = ut
    dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
    return sqrt(dx * dx + dy * dy + dz * dz)