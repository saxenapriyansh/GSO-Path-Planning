from __future__ import division
import time
import os
import subprocess
from math import isinf, sqrt, pi
import numpy as np
import matplotlib.pyplot as plt
import config_user as gl
import config_program
import all_functions as fcn
import GSO

def deleteStaticTarget(point):
    pointX, pointY, pointZ = point[0], point[1], point[2]

    for index, x in enumerate(gl.goals):
        if x[0] == pointX and x[1] == pointY and x[2] == pointZ:
            gl.goals = np.delete(gl.goals, index, 0)
            break

    gl.numGoals = len(gl.goals)


    if gl.goal[0] == pointX and gl.goal[1] == pointY and gl.goal[2] == pointZ:
        hyp = []
        for i in xrange(0, gl.numGoals):
            gX, gY, gZ = gl.goals[i, 0], gl.goals[i, 1], gl.goals[i, 2]
            xdist, ydist, zdist = gX - gl.start[0], gY - gl.start[1], gZ - gl.start[2]
            hyp.append(sqrt(xdist ** 2 + ydist ** 2 + zdist ** 2))

        goalindex = hyp.index(min(hyp))
        gl.goal = (gl.goals[goalindex, 0], gl.goals[goalindex, 1], gl.goals[goalindex, 2])

    # Plot movement and save figure
    if makeMovie:
        fname = ('_tmp%05d.' + gl.imgformat) % gl.stepCount
        print gl.stepCount, " created"
        plt.savefig(fname, dpi=gl.dpi, bbox_inches='tight')
        frames.append(fname)
        gl.stepCount = gl.stepCount + 1

    if gl.makeFigure:
        gl.ax1.plot([xOld, xNew], [yOld, yNew], [zOld, zNew], linewidth=2, c='#5DA5DA', zorder=0)


def addStaticTarget(point):
    pointX, pointY, pointZ = point[0], point[1], point[2]

    newgoals = np.zeros((1, 4))
    newgoals[0, 0], newgoals[0, 1], newgoals[0, 2], newgoals[0, 3] = staticX, staticY, staticZ, fcn.cantor(staticX, staticY, staticZ)
    gl.goals = np.vstack((gl.goals, newgoals))

    gl.numGoals = len(gl.goals)

    # Finding nearest goal
    hyp = []
    for i in xrange(0, gl.numGoals):
        gX, gY, gZ = gl.goals[i, 0], gl.goals[i, 1], gl.goals[i, 2]
        xdist, ydist, zdist = gX - gl.start[0], gY - gl.start[1], gZ - gl.start[2]
        hyp.append(sqrt(xdist ** 2 + ydist ** 2 + zdist ** 2))

    goalindex = hyp.index(min(hyp))
    gl.goal = (gl.goals[goalindex, 0], gl.goals[goalindex, 1], gl.goals[goalindex, 2])

    # Plot movement and save figure
    if makeMovie:
        fname = ('_tmp%05d.' + gl.imgformat) % gl.stepCount
        print gl.stepCount, " created"
        plt.savefig(fname, dpi=gl.dpi, bbox_inches='tight')
        frames.append(fname)
        gl.stepCount = gl.stepCount + 1

    if gl.makeFigure:
        gl.ax1.plot([xOld, xNew], [yOld, yNew], [zOld, zNew], linewidth=2, c='#5DA5DA', zorder=0)



# To reload settings for multiple trials
if gl.testingMode:
    reload(gl)
    reload(config_program)
    reload(fcn)

# Creating local copies of constants
sizeX, sizeY, sizeZ, cX, cY, cZ = gl.sizeX, gl.sizeY, gl.sizeZ, gl.cX, gl.cY, gl.cZ
searchRadius, useMovingGoals = gl.searchRadius, gl.useMovingGoals
makeRandObs, makeFigure, makeMovie, numlevels = gl.makeRandObs, gl.makeFigure, gl.makeMovie, gl.numlevels
minObs, maxObs, maxPercent, seedDyn, seedStatic = gl.minObs, gl.maxObs, gl.maxPercent, gl.seedDyn, gl.seedStatic
initX, initY, initZ, T, rXdim, rYdim, rZdim = gl.initX, gl.initY, gl.initZ, gl.T, gl.rXdim, gl.rYdim, gl.rZdim
rXstart, rYstart, rZstart = gl.rXstart, gl.rYstart, gl.rZstart
refinementDistance = gl.refinementDistance

T_obs = gl.T_obs
useMovingObs = gl.useMovingObs
obsX, obsY, obsZ = gl.obsX , gl.obsY, gl.obsZ
######################################
staticX, staticY, staticZ = gl.staticX, gl.staticY, gl.staticZ
######################################

if makeMovie:   frames = []


""" Setup abstract levels and variables for performance testing """
#L = fcn.setupLevels()
time_findPath = []
total_cost = 0
final_pathX = [gl.start[0]]
final_pathY = [gl.start[1]]
final_pathZ = [gl.start[2]]

tic1 = time.time()
""" Begin main algorithm """
for idx in xrange(0, gl.numGoals):                      # for each goal
    L = fcn.setupLevels()
    xNew, yNew, zNew = gl.start                         # get current location
    fcn.searchAndUpdate(xNew,yNew,zNew)                 # search for obstacles

    while gl.start != gl.goal:

        """ Compute path, smooth it, make a spline, and divide into a series of adjacent points to follow """
        tic = time.clock()    # start timer
        path = GSO.run_gso(gl.start, gl.goal)
        path.reverse()

        # path = fcn.postSmoothPath(path)
        # path = fcn.CatmullRomSpline(path)
        # path = fcn.simulateUAVmovement(path)

        findPathTime = time.clock() - tic   # end timer
        time_findPath.append(findPathTime)  # record time
        if gl.stepCount == 1:
            initialFindPathTime = findPathTime  # record time to find

        xOrig, yOrig, zOrig = gl.start      # to identify when leaving refinement region
        dfs = 0                             # distance from start, used to identify when path needs to be updated
        goalMoved = False                   # indicates whether or not the goal has moved
        validPath = True                    # indicates whether or not path being followed is still valid

        while not goalMoved and validPath and gl.start != gl.goal and path:
            q_time_static = fcn.cantor(staticX, staticY, staticZ)

            highExecuted, lowExecuted = False, False
            if len(path) >= 2:
                low, high = np.random.randint(1, len(path), size=2)
                low, high = min(low, high), max(low, high)
                flagLowHigh = True
            else:
                flagLowHigh = False

            # Follow those points until path is invalidated or we reach end of refinement region
            pathLen = 0
            for point in path:
                ################################################
                # Time Varying Goal
                if flagLowHigh and pathLen == low:
                    if q_time_static not in gl.goalsVisited:
                        if q_time_static in gl.goalhandles:
                            if gl.goalhandles[q_time_static] is not None:
                                if q_time_static in gl.goalhandles:
                                    if gl.numGoals > 1:
                                        gl.goalhandles[q_time_static].remove()
                                        deleteStaticTarget((staticX, staticY, staticZ))
                                        lowExecuted = True
                                    else:
                                        # Hide Goal
                                        gl.goalhandles[q_time_static].remove()
                                        gl.goals = []
                                        gl.numGoals = 0
                                        gl.goal = []
                                        lowExecuted = True

                                        # Halt/ No Operation
                                        while pathLen != high:
                                            if makeMovie:
                                                fname = ('_tmp%05d.' + gl.imgformat) % gl.stepCount
                                                plt.savefig(fname, dpi=gl.dpi, bbox_inches='tight')
                                                frames.append(fname)
                                                gl.stepCount = gl.stepCount + 1

                                            if gl.makeFigure:
                                                gl.ax1.plot([xOld, xNew], [yOld, yNew], [zOld, zNew], linewidth=2,
                                                            c='#5DA5DA', zorder=0)
                                            pathLen = pathLen + 1

                                        # Show Goal
                                        gl.goalhandles[q_time_static] = gl.ax1.scatter(staticX, staticY, staticZ, c='b')

                                        newgoals = np.zeros((1, 4))
                                        newgoals[0, 0], newgoals[0, 1], newgoals[0, 2], newgoals[
                                            0, 3] = staticX, staticY, staticZ, fcn.cantor(staticX, staticY, staticZ)
                                        gl.goals = newgoals

                                        gl.numGoals = len(gl.goals)

                                        hyp = []
                                        for i in xrange(0, gl.numGoals):
                                            gX, gY, gZ = gl.goals[i, 0], gl.goals[i, 1], gl.goals[i, 2]
                                            xdist, ydist, zdist = gX - gl.start[0], gY - gl.start[1], gZ - gl.start[2]
                                            hyp.append(sqrt(xdist ** 2 + ydist ** 2 + zdist ** 2))

                                        goalindex = hyp.index(min(hyp))
                                        gl.goal = (
                                            gl.goals[goalindex, 0], gl.goals[goalindex, 1], gl.goals[goalindex, 2])

                                        # Plot movement and save figure
                                        if makeMovie:
                                            fname = ('_tmp%05d.' + gl.imgformat) % gl.stepCount
                                            plt.savefig(fname, dpi=gl.dpi, bbox_inches='tight')
                                            frames.append(fname)
                                            gl.stepCount = gl.stepCount + 1

                                        if gl.makeFigure:
                                            gl.ax1.plot([xOld, xNew], [yOld, yNew], [zOld, zNew], linewidth=2,
                                                        c='#5DA5DA', zorder=0)
                                        highExecuted = True

                if flagLowHigh and not highExecuted and pathLen == high:
                    if q_time_static not in gl.goalsVisited:
                        gl.goalhandles[q_time_static] = gl.ax1.scatter(staticX, staticY, staticZ, c='b')
                        addStaticTarget((staticX, staticY, staticZ))
                        highExecuted = True
                ################################################

                # Save current position, then move to next point
                xOld, yOld, zOld = xNew, yNew, zNew
                xNew, yNew, zNew = path.pop()
                gl.oldstart = gl.start
                gl.start = (round(xNew), round(yNew), round(zNew))   # update start coordinate

                # Update distance from start
                dx, dy, dz = xOrig-xNew, yOrig-yNew, zOrig-zNew
                dfs = sqrt(dx**2 + dy**2 + dz**2)

                # Plot movement and save figure
                if makeMovie:
                    fname = ('_tmp%05d.'+gl.imgformat) %gl.stepCount
                    plt.savefig(fname,dpi=gl.dpi,bbox_inches='tight')
                    frames.append(fname)
                    print gl.stepCount, " created"
                    gl.stepCount = gl.stepCount + 1
                if gl.makeFigure:
                    gl.ax1.plot([xOld,xNew], [yOld,yNew], [zOld,zNew], linewidth=2, c='#5DA5DA',zorder=0)

                # Update total cost of path
                total_cost += L[0].computeCost((xOld, yOld, zOld), (xNew, yNew, zNew), False)

                final_pathX.append(xNew)
                final_pathY.append(yNew)
                final_pathZ.append(zNew)


                # Generate random obstacles
                if makeRandObs:
                    fcn.genRandObs(minObs,maxObs,maxPercent,seedDyn)

                # Moving obstacle execution
                if useMovingObs:
                    for i in xrange(0, len(obsX)):  obsMoved = fcn.movingObs(obsX[i], obsY[i], obsZ[i], T_obs[i])

                # Moving goal execution
                if useMovingGoals:
                    for i in xrange(0,len(initX)):  goalMoved = fcn.movingGoal(initX[i], initY[i], initZ[i], T[i])

                # Update counter used for the two preceding functions
                if not makeMovie: gl.stepCount += 1
                pathLen = pathLen + 1

                # Check if there's any obstacles within search radius if we've moved to a different node
                if gl.oldstart != gl.start and not fcn.searchAndUpdate(xNew, yNew, zNew, path):
                    validPath=False
                    break

                # Check if next movement takes us outside of refinement region
                if dfs+1 >= refinementDistance/2 or len(path)<1:
                    validPath = False
                    break

            if not highExecuted and lowExecuted and q_time_static not in gl.goalsVisited:
                gl.goalhandles[q_time_static] = gl.ax1.scatter(staticX, staticY, staticZ, c='b')
                addStaticTarget((staticX, staticY, staticZ))

    if len(gl.goals) > 1:
        print(gl.numGoals-1, ' goals left...')

        # Identify rows in goals array matching current goal
        k1 = np.where(gl.goals[:,0]==gl.goal[0])
        k2 = np.where(gl.goals[:,1]==gl.goal[1])
        k3 = np.where(gl.goals[:,2]==gl.goal[2])

        # Whichever row shows up in k1, k2, and k3 is the row with the current goal
        k = np.intersect1d(np.intersect1d(k1,k2),k3)

        gl.goalsVisited.append(gl.goals[k,3])           # save its goal ID
        gl.goals = np.delete(gl.goals, k, 0)            # delete that row
        gl.numGoals -= 1

        # Find next closest goal with respect to straight line distance
        hyp = {}
        for idx, row in enumerate(gl.goals):
            gx, gy, gz = row[0], row[1], row[2]
            xdist, ydist, zdist = gx-gl.start[0], gy-gl.start[1], gz-gl.start[2]
            hyp[idx] = sqrt(xdist**2 + ydist**2 + zdist**2)

        idx, __ = min(hyp.items(), key=lambda x:x[1])
        gl.goal = (gl.goals[idx,0], gl.goals[idx,1], gl.goals[idx,2])

# Get averages, in milliseconds
mean_time_findPath = 1000*sum(time_findPath) / len(time_findPath)


def hdstar_outputs():
    return total_cost, gl.closed_list, mean_time_findPath, initialFindPathTime*1000

if not gl.testingMode:
    print 'Run succeeded!\n'
    print 'Elapsed time: ' + str(time.time() - tic1) + ' seconds'
    print 'Total cost: ' + str(total_cost)
    print 'Mean Path-finding Time: ' + str(mean_time_findPath) + ' ms'
    print 'Expanded nodes: ' + str(gl.closed_list)




if makeMovie:
    # Save a few extra still frame so video doesn't end abruptly
    print 'Making video....'
    for i in xrange(1,11):
        idx = gl.stepCount+i
        fname = ('_tmp%05d.'+gl.imgformat) %idx
        plt.savefig(fname,dpi=gl.dpi,bbox_inches='tight')
        frames.append(fname)

    # Then make movie
    command = ('mencoder','mf://_tmp*.'+gl.imgformat,'-mf',
           'type='+gl.imgformat+':w=800:h=600:fps='+str(gl.fps),'-ovc',
            'lavc','-lavcopts','vcodec=mpeg4','-oac','copy','-o',gl.vidname+'.avi')
    # subprocess.check_call(command)
    # for fname in frames: os.remove(fname) # remove temporary images

    # print 'Video complete!'

if makeFigure:
    plt.savefig('GSOFig.pdf',bbox_inches='tight')
    print 'Figure is open. Close figure to end script'
    plt.show()


print final_pathX
print final_pathY
print final_pathZ