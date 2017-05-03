from random import random, randint
import math

def winePrice(rating, age):
	peak_age = rating - 50
	price = rating / 2
	if age > peak_age:
		price = price * (5 - (age - peak_age))
	else:
		price = price * (5 * ((age + 1) / peak_age))

	if price < 0:
		price = 0

	return price

def wineSet1():
	rows = []

	for i in range(300):
		rating = random() * 50 + 50
		age = random() * 50

		price = winePrice(rating, age)

		price *= (random() * 0.4 + 0.8)

		rows.append({'input':(rating, age),
			'result': price})

	return rows

def euclidean(v1, v2):
	d = 0.0
	for i in range(len(v1)):
		d += (v1[i] - v2[i]) ** 2

	return math.sqrt(d)

def getDistances(data, vec1):
	distanceList = []

	for i in range(len(data)):
		vec2 = data[i]['input']
		distanceList.append((euclidean(vec1, vec2), i))

	distanceList.sort()
	return distanceList

def KNN(data, vec1, k = 5):
	dList = getDistances(data, vec1)
	avg = 0.0

	for i in range(k):
		idx = dList[i][1]
		avg += data[idx]['result']

	avg = avg / k
	return avg

def inverseWeight(dist, num = 1.0, const = 0.1):
	return num / (dist + const)

def subtractWeight(dist, const = 1.0):
	if dist > const:
		return 0
	else:
		return const - dist

def gaussian(dist, sigma = 10.0):
	return math.e ** (-dist ** 2 / (2 * sigma ** 2))

def weightedKNN(data, vec1, k = 5, weightF = gaussian):
	dList = getDistances(data, vec1)
	avg = 0.0
	totalWeight = 0.0

	for i in range(k):
		dist = dList[i][0]
		idx = dList[i][1]
		weight = weightF(dist)
		avg += weight * data[idx]['result']
		totalWeight += weight

	avg = avg / totalWeight
	return avg

def divideData(data, test = 0.05):
	trainSet = []
	testSet = []
	for row in data:
		if random() < test:
			testSet.append(row)
		else:
			trainSet.append(row)
	return trainSet, testSet

def testAlgorithm(algF, trainSet, testSet):
	error = 0.0

	for row in testSet:
		guess = algF(trainSet, row['input'])
		error += (row['result'] - guess) ** 2

	return error / len(testSet)

def crossValidate(algF, data, trials = 100, test = 0.05):
	error = 0.0
	for i in range(trials):
		trainSet, testSet = divideData(data, test)
		error += testAlgorithm(algF, trainSet, testSet)

	return error / trials

def wineSet2():
	rows = []

	for i in range(300):
		rating = random() * 50 + 50
		age = random() * 50

		aisle = float(randint(1, 20))
		bottleSize = [375.0, 750.0, 1500.0, 3000.0][randint(0, 3)]
		price = winePrice(rating, age)
		price *= (bottleSize / 750)
		price *= (random() * 0.9 + 0.2)
		rows.append({'input': (rating, age, aisle, bottleSize), 'result': price})

	return rows

def rescale(data, scale):
	scaleData = []
	for row in data:
		scaled = [scale[i] * row['input'][i] for i in range(len(scale))]
		scaleData.append({'input': scaled, 'result': row['result']})

	return scaleData

def createCostFunction(algF, data):
	def costF(scale):
		sdata = rescale(data, scale)
		return crossValidate(algF, sdata, trials = 10)
	return costF

weightDomain = [(0, 20)] * 4

def wineSet3():
	rows = wineSet1()
	for row in rows:
		if random() < 0.5:
			row['result'] *= 0.6
	return rows

def probGuess(data, vec1, low, high, k = 5, weightF = gaussian):
	dList = getDistances(data, vec1)
	nWeight = 0.0
	tWeight = 0.0

	for i in range(k):
		dist = dList[i][0]
		idx = dList[i][1]
		weight = weightF(dist)
		v = data[idx]['result']

		if v >= low and v <= high:
			nWeight += weight
		tWeight += weight

	if tWeight == 0:
		return 0

	return nWeight / tWeight

from pylab import * 

def cumulativeGraph(data, vec1, high, k = 5, weightF = gaussian):
	t1 = arange(0.0, high, 0.1)
	cprob = array([probGuess(data, vec1, 0, v, k, weightF) for v in t1])
	plot(t1, cprob)
	show()
