def removeLoops(Paths):
    path = Paths
    psize = len(Paths)
    i=0
    while(i<psize):
        cur = path[i]
        for j in range(i+1, psize):
            if(cur == path[j]):
                path[i:j] = ()
                psize = len(path)
                break
        i= i+1
    return path