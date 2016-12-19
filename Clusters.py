def readFile(filename):
	lines = [line for line in file(filename)]

	# First line is the column titles
	colnames = lines[0].strip().split('\t')[1:]

	rownames = []
	data = []
	for line in lines[1:]:
		p = line.strip().split('\t')
		# First column in each row is the rowname
		rownames.append(p[0])
		# The data for this row is the remainder of the row
		data.append([float(x) for x in p[1:]])

	return rownames, colnames, data

from math import sqrt
def pearson(v1, v2):
	# Simple sums
	sum1 = sum(v1)
	sum2 = sum(v2)

	# Sums of the squares
	sum1Sq = sum([pow(v, 2) for v in v1])
	sum2Sq = sum([pow(v, 2) for v in v2])

	# Sum of the products
	pSum = sum([v1[i]*v2[i] for i in range(len(v1))])

	# Caluculate Pearson score
	num = pSum - (sum1 * sum2 / len(v1))
	den = sqrt((sum1Sq - pow(sum1, 2) / len(v1)) * (sum2Sq - pow(sum2, 2) / len(v1)))
	if den ==0:
		return 0

	return 1.0 - num / den

class biCluster:
	def __init__(self, vec, left = None, right = None, distance = 0.0, id = None):
		self.left = left
		self.right = right
		self.vec = vec
		self.id = id
		self.distance = distance

def hCluster(rows, distance = pearson):
	distances = {}
	currentClustId = -1

	clust = [biCluster(rows[i], id = i) for i in range(len(rows))]

	while len(clust) > 1:
		lowestPair = (0, 1)
		closest = distance(clust[0].vec, clust[1].vec)

		# Loop through every pair looking for the smallest distance
		for i in range(len(clust)):
			for j in range(i + 1, len(clust)):
				# Distance is the cache of distance calculations
				if (clust[i].id, clust[j].id) not in distances:
					distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)

				d = distances[(clust[i].id, clust[j].id)]

				if d < closest:
					closest = d
					lowestPair = (i, j)

		# Calculate the average of the two clusters
		mergeVec = [
		(clust[lowestPair[0]].vec[i] + clust[lowestPair[1]].vec[i]) / 2.0
		for i in range(len(clust[0].vec))
		]

		# Create the new cluster
		newCluster = biCluster(mergeVec, left = clust[lowestPair[0]],
							right = clust[lowestPair[1]],
							distance = closest, id = currentClustId)

		# Cluster ids that weren't in the original set are negative
		currentClustId -= 1
		del clust[lowestPair[1]]
		del clust[lowestPair[0]]
		clust.append(newCluster)

	return clust[0]

def printClust(clust, labels = None, n = 0):
	# Indent to make a hierarchy layout
	for i in range(n): print ' ',

	if clust.id < 0:
	# Negative id means that this is branch
		print '-'

	else:
		# Positive id means that this is an endpoint
		if labels == None: print clust.id
		else: print labels[clust.id]

	# Now print the right and left branches
	if clust.left != None: printClust(clust.left, labels = labels, n = n + 1)
	if clust.right != None: printClust(clust.right, labels = labels, n = n + 1)

from PIL import Image, ImageDraw

def getHeight(clust):
	# Is this an endpoint, if so the height is just 1
	if clust.left == None and clust.right == None: return 1

	# Otherwise the height is the same of the heights of each branch
	return getHeight(clust.left) + getHeight(clust.right)

def getDepth(clust):
	# The distance of an endpoint is 0.0
	if clust.left == None and clust.right == None: return 0

	# The depth of a branch is the greater of its two sides plus its own distance
	return max(getDepth(clust.left), getDepth(clust.right)) + clust.distance

def drawDendrogram(clust, labels, bmp = 'Clusters.bmp'):
	# Height and width
	h = getHeight(clust) * 20
	w = 1200

	depth = getDepth(clust)

	# Width is fixes, so scale distances accordingly
	scaling = float(w - 150) / depth

	# Create a new image with a white background
	img = Image.new('RGB', (w, h), (255, 255, 255))
	draw = ImageDraw.Draw(img)

	# Draw the first node
	drawNode(draw, clust, 10, (h / 2), scaling, labels)
	img.save(bmp)

def drawNode(draw, clust, x, y, scaling, labels):
	if clust.id < 0:
		h1 = getHeight(clust.left) * 20
		h2 = getHeight(clust.right) * 20
		top = y - (h1 + h2) / 2
		bottom = y + (h1 + h2) / 2
		# Line length
		ll = clust.distance * scaling
		# Vertical line from this cluster to children
		draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill = (255, 0, 0))

		# Horizontal line to left item
		draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill = (255, 0, 0))

		# Horizontal line to right item
		draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2), fill = (255, 0, 0))

		# Call the function to draw the left and right nodes
		drawNode(draw, clust.left, x + ll, top + h1 / 2, scaling, labels)
		drawNode(draw, clust.right, x + ll, bottom - h2 / 2, scaling, labels)

	else:
		# If this is an endpoint, draw the item label
		draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))

def rotateMatrix(data):
	newData = []
	for i in range(len(data[0])):
		newRow = [data[j][i] for j in range(len(data))]
		newData.append(newRow)

	return newData

import random

def kCluster(rows, distance = pearson, k = 4):
	# Deetermine the minomum and maxmium values for each point
	ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]

	# Create k randomly placed centroids
	clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0] for i in range(len(rows[0]))] for j in range(k)]

	lastMatches = None
	for t in range(100):
		print 'Iteration %d' % t
		bestMatches = [[] for i in range(k)]

		# Find which centroid is the closest for each row
		for j in range(len(rows)):
			row = rows[j]
			bestMatch = 0
			for i in range(k):
				d = distance(clusters[i], row)
				if d < distance(clusters[bestMatch], row):
					bestMatch = i

			bestMatches[bestMatch].append(j)

		# If the results are the same as last time this is done
		if bestMatches == lastMatches:
			break

		lastMatches = bestMatches

		# Move the centroids to the average of their members
		for i in range(k):
			avgs = [0.0] * len(rows[0])
			if len(bestMatches[i]) > 0:
				for rowId in bestMatches[i]:
					for m in range(len(rows[rowId])):
						avgs[m] += rows[rowId][m]

				for j in range(len(avgs)):
					avgs[j] /= len(bestMatches[i])

				clusters[i] = avgs


	return bestMatches

def tanimoto(v1, v2):
	c1, c2, share = 0, 0, 0
	for i in range(len(v1)):
		if v1[i] != 0: c1 += 1
		if v2[i] != 0: c2 += 1
		if v1[i] != 0 and v2[i] != 0: share += 1

	return 1.0 - (float(share) / (c2 + c2 - share))

# Multidimentional scaling
def scaleDown(data, distance = pearson, rate = 0.01):
	n = len(data)

	# The real distances between every pair of items
	realDist = [[distance(data[i], data[j]) for j in range(n)] for i in range(0, n)]
	outerSum = 0.0

	# Randomly initialize the starting points of the locations in 2D
	loc = [[random.random(), random.random()] for i in range(n)]
	fakeDist = [[0.0 for j in range(n)] for i in range(n)]

	lastError = None
	for m in range(0, 1000):
		# Find projected distances
		for i in range(n):
			for j in range(n):
				fakeDist[i][j] = sqrt(sum([pow(loc[i][x] - loc[j][x], 2) for x in range(len(loc[i]))]))

		# Move points
		grad = [[0.0, 0.0] for i in range(n)]

		totalError = 0
		for k in range(n):
			for j in range(n):
				if k == j: continue
				# The error is percent difference between the distances
				errorTerm = 0
				if realDist[j][k] == 0:
					errorTerm = 0
				else:
					errorTerm = (fakeDist[j][k] - realDist[j][k]) / realDist[j][k]

				# Each point needs to be moved away from or towards the other point in proportion to thow much error it has
				grad[k][0] += ((loc[k][0] - loc[j][0]) / fakeDist[j][k]) * errorTerm
				grad[k][1] += ((loc[k][1] - loc[j][1]) / fakeDist[j][k]) * errorTerm

				totalError += abs(errorTerm)

		print totalError

		# If the answer got worse by moving the points we are done
		if lastError and lastError < totalError: break
		lastError = totalError

		# Move each of the points by the learning rate times the gradient
		for k in range(n):
			loc[k][0] -= rate * grad[k][0]
			loc[k][1] -= rate * grad[k][1]

	return loc

def draw2D(data, labels, bmp='MultDimen2D.bmp'):
	img = Image.new('RGB', (2000, 2000), (255, 255, 255))
	draw = ImageDraw.Draw(img)
	for i in range(len(data)):
		x = (data[i][0] + 0.5) * 1000
		y = (data[i][1] + 0.5) * 1000
		draw.text((x, y), labels[i], (0, 0, 0))

	img.save(bmp)

def manhattan(v1, v2):

	r = sum([abs(v1[i] - v2[i]) for i in range(len(v1))])

	return r

def kClusterWithTotalDistance(rows, distance = pearson, k = 4):
	# Deetermine the minomum and maxmium values for each point
	ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]

	# Create k randomly placed centroids
	centroids = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0] for i in range(len(rows[0]))] for j in range(k)]

	lastMatches = None
	for t in range(100):
		print 'Iteration %d' % t
		bestMatches = [[] for i in range(k)]
		totalDistances = [0.0 for i in range(k)]

		# Find which centroid is the closest for each row
		for j in range(len(rows)):
			row = rows[j]
			bestMatch = 0
			minimalDistance = 0;
			for i in range(k):
				d = distance(centroids[i], row)
				if d <= distance(centroids[bestMatch], row):
					bestMatch = i
					minimalDistance = d

			bestMatches[bestMatch].append(j)
			totalDistances[bestMatch] += minimalDistance

		# If the results are the same as last time this is done
		if bestMatches == lastMatches:
			break

		lastMatches = bestMatches

		# Move the centroids to the average of their members
		for i in range(k):
			avgs = [0.0] * len(rows[0])
			if len(bestMatches[i]) > 0:
				for rowId in bestMatches[i]:
					for m in range(len(rows[rowId])):
						avgs[m] += rows[rowId][m]

				for j in range(len(avgs)):
					avgs[j] /= len(bestMatches[i])

				centroids[i] = avgs


	return bestMatches, totalDistances

