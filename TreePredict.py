myData= [line.split('\t') for line in file('DecisionTreeExample.txt')]

class DecisionNode:
	def __init__(self, col = -1, value = None, results = None, tb = None, fb = None):
		self.col = col
		self.value = value
		self.results = results
		self.tb = tb
		self.fb = fb

def divideSet(rows, column, value):
	splitFunction = None
	if isinstance(value, int) or isinstance(value, float):
		splitFunction = lambda row: row[column] >= value
	else:
		splitFunction = lambda row: row[column] == value

	set1 = [row for row in rows if splitFunction(row)]
	set2 = [row for row in rows if not splitFunction(row)]

	return (set1, set2)

def uniqueCounts(rows):
	results = {}
	for row in rows:
		r = row[len(row) - 1]
		if r not in results:
			results[r] = 0

		results[r] += 1

	return results

# Probability that a randomly placed item will be in the wrong category
def giniImpurity(rows):
	total = len(rows)
	counts = uniqueCounts(rows)
	imp = 0
	for k1 in counts:
		p1 = float(counts[k1]) / total

		for k2 in counts:
			if k1 == k2:
				continue

			p2 = float(counts[k2]) / total

			imp += p1 * p2

	return imp

# Entropy is the sum of p(x)log(p(x)) accross all the different possible results
def entropy(rows):
	from math import log
	log2 = lambda x: log(x) / log(2)

	results = uniqueCounts(rows)

	ent = 0.0
	for r in results.keys():
		p = float(results[r]) / len(rows)
		ent = ent - p * log2(p)

	return ent

def buildTree(rows, scoreF = entropy):
	if len(rows) == 0:
		return DecisionNode()

	currentScore = scoreF(rows)

	# Setup some variables to track the best criteria
	bestGain = 0.0
	bestCriteria = None
	bestSets = None

	columnCount = len(rows[0]) - 1

	for col in range(0, columnCount):
		columnValues = {}

		for row in rows:
			columnValues[row[col]] = 1

		for value in columnValues.keys():
			(set1, set2) = divideSet(rows, col, value)

			p = float(len(set1)) / len(rows)
			gain = currentScore - p * scoreF(set1) - (1- p) * scoreF(set2)

			if gain > bestGain and len(set1) > 0 and len(set2) > 0:
				bestGain = gain
				bestCriteria = (col, value)
				bestSets = (set1, set2)

	if bestGain > 0:
		trueBranch = buildTree(bestSets[0])
		falseBranch = buildTree(bestSets[1])
		return DecisionNode(col = bestCriteria[0], value = bestCriteria[1], tb = trueBranch, fb = falseBranch)

	else:
		return DecisionNode(results = uniqueCounts(rows))

