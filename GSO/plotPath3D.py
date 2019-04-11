from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

def plotPath3D(path, GoalNode):
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	x, y, z = [],[],[]
	for coordinate in path:
		x.append(coordinate[0])
		y.append(coordinate[1])
		z.append(coordinate[2])

	a = []
	b = []
	c = []
	for item in x:
		a.append(float(item))
	for item in y:
		b.append(float(item))
	for item in z:
		c.append(float(item))

	r = np.array(a)
	s = np.array(b)
	t = np.array(c)


	ax.set_xlabel("x axis")
	ax.set_ylabel("y axis")
	ax.set_zlabel("z axis")
	ax.scatter(r, s, zs=t, s=200)
	ax.plot3D(r, s, z)
	ax.scatter(GoalNode[0], GoalNode[1], zs=GoalNode[2], s=200)
	plt.show()