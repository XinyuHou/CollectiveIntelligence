from numpy import *

def difCost(a, b):
	dif = 0
	for i in range(shape(a)[0]):
		for j in range(shape(a)[1]):
			dif += pow(a[i,j] - b[i,j], 2)

	return dif

def factorize(v, pc = 10, iter = 50):
	ic = shape(v)[0]
	fc = shape(v)[1]

	w = matrix([[random.random() for j in range(pc)] for i in range(ic)])
	h = matrix([[random.random() for j in range(fc)] for i in range(pc)])

	for i in range(iter):
		wh = w * h

		cost = difCost(v, wh)

		if i % 10 == 0:
			print cost

		if cost == 0:
			break

		hn = (transpose(w) * v)
		hd = (transpose(w) * w * h)

		h = matrix(array(h) * array(hn) / array(hd))
		where_are_NaNs = isnan(h)
		h[where_are_NaNs] = 0

		wn = (v * transpose(h))
		wd = (w * h * transpose(h))

		w = matrix(array(w) * array(wn) / array(wd))
		where_are_NaNs = isnan(w)
		w[where_are_NaNs] = 0

	return w, h
