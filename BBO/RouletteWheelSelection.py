import numpy as np

def RouletteWheelSelection(P):
	r = np.random.rand()
	c = np.cumsum(P)
	j = np.where(r <= c)
	return j[0].tolist()[0]