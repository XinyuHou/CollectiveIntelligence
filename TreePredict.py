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

def printTree(tree, indent = ''):
	if tree.results != None:
		print str(tree.results)

	else:
		print str(tree.col) + ':' + str(tree.value) + '? '

		print indent + 'T -> ',
		printTree(tree.tb, indent + '	')

		print indent + 'F -> ',
		printTree(tree.fb, indent + '	')

def getWidth(tree):
	if tree.tb == None and tree.fb == None: return 1

	return getWidth(tree.tb) + getWidth(tree.fb)

def getDepth(tree):
	if tree.tb == None and tree.fb == None: return 0

	return max(getDepth(tree.tb), getDepth(tree.fb)) + 1

from PIL import Image, ImageDraw
def drawTree(tree, bmp = 'DecisionTree.bmp'):
	w = getWidth(tree) * 100
	h = getDepth(tree) * 100 + 120

	img = Image.new('RGB', (w, h), (255, 255, 255))
	draw = ImageDraw.Draw(img)

	drawNode(draw, tree, w / 2, 20)
	img.save(bmp)

def drawNode(draw, tree, x, y):
	if tree.results == None:
		w1 = getWidth(tree.fb) * 100
		w2 = getWidth(tree.tb) * 100

		left = x - (w1 + w2) / 2
		right = x + (w1 + w2) / 2

		draw.text((x - 20, y - 10), str(tree.col) + ':' + str(tree.value), (0, 0, 0))

		draw.line((x, y, left + w1 / 2, y + 100), fill = (255, 0, 0))
		draw.line((x, y, right - w2 / 2, y + 100), fill = (255, 0, 0))

		drawNode(draw, tree.fb, left + w1 / 2, y + 100)
		drawNode(draw, tree.tb, right - w2 / 2, y + 100)
	else:
		txt = '\n'.join(['%s : %d' %v for v in tree.results.items()])
		draw.text((x - 20, y), txt, (0, 0, 0))

def classify(observation, tree):
	if tree.results != None:
		return tree.results
	else:
		v = observation[tree.col]
		branch = None

		if isinstance(v, int) or isinstance(v, float):
			if v >= tree.value:
				branch = tree.tb
			else:
				branch = tree.fb
		else:
			if v == tree.value:
				branch = tree.tb
			else:
				branch = tree.fb

		return classify(observation, branch)

def prune(tree, minGain):
	if tree.tb.results == None:
		prune(tree.tb, minGain)
	if tree.fb.results == None:
		prune(tree.fb, minGain)

	if tree.tb.results != None and tree.fb.results != None:
		tb, fb = [], []

		for v, c in tree.tb.results.items():
			tb += [[v]] * c
		for v, c in tree.fb.results.items():
			fb += [[v]] * c

		delta = entropy(tb + fb) - (entropy(tb) + entropy(fb))

		if delta < minGain:
			tree.tb, tree.fb = None, None
			tree.results = uniqueCounts(tb + fb)

def missingDataClassify(observation, tree):
	if tree.results != None:
		return tree.results
	else:
		v = observation[tree.col]
		if v == None:
			tr, fr = missingDataClassify(observation, tree.tb), missingDataClassify(observation, tree.fb)
			tCount = sum(tr.values())
			fCount = sum(fr.values())
			tw = float(tCount) / (tCount + fCount)
			fw = float(fCount) / (tCount + fCount)

			result = {}

			for k, v in tr.items():
				result[k] = v * tw
			for k, v in fr.items():
				result[k] = result.setdefault(k, 0) + (v * fw)
			return result
		else:
			if isinstance(v, int) or isinstance(v, float):
				if v >= tree.value:
					branch = tree.tb
				else:
					branch = tree.fb
			else:
				if v == tree.value:
					branch = tree.tb
				else:
					branch = tree.fb

			return missingDataClassify(observation, branch)

def variance(rows):
	if len(rows) == 0:
		return 0

	data = [float(row[len(row) - 1]) for row in rows]
	mean = sum(data) / len(data)
	variance = sum([(d - mean) ** 2 for d in data]) / len(data)
	return variance

def missingRangeDataClassify(observation, tree):
	if tree.results != None:
		return tree.results
	else:
		v = observation[tree.col]
		if v == None:
			tr, fr = missingRangeDataClassify(observation, tree.tb), missingRangeDataClassify(observation, tree.fb)
			tCount = sum(tr.values())
			fCount = sum(fr.values())
			tw = float(tCount) / (tCount + fCount)
			fw = float(fCount) / (tCount + fCount)

			result = {}

			for k, v in tr.items():
				result[k] = v * tw
			for k, v in fr.items():
				result[k] = result.setdefault(k, 0) + (v * fw)
			return result
		elif type(v) is tuple:
			if isinstance(v[0], int) or isinstance(v[0], float) and isinstance(v[1], int) or isinstance(v[1], float):
				min = float(v[0])
				max = float(v[1])
				if float(tree.value) > max:
					branch = tree.fb
					return missingRangeDataClassify(observation, branch)
				elif float(tree.value) <= min:
					branch = tree.tb
					return missingRangeDataClassify(observation, branch)
				else:
					tr, fr = missingRangeDataClassify(observation, tree.tb), missingRangeDataClassify(observation, tree.fb)
					tCount = sum(tr.values())
					fCount = sum(fr.values())
					tw = float(tCount) / (tCount + fCount)
					fw = float(fCount) / (tCount + fCount)
					tp = float(max - float(tree.value)) / (max - min) 
					fp = float(float(tree.value) - min) / (max - min) 

					result = {}

					for k, v in tr.items():
						result[k] = v * tw * tp
					for k, v in fr.items():
						result[k] = result.setdefault(k, 0) + (v * fw * fp)
					return result

		else:
			if isinstance(v, int) or isinstance(v, float):
				if v >= tree.value:
					branch = tree.tb
				else:
					branch = tree.fb
			else:
				if v == tree.value:
					branch = tree.tb
				else:
					branch = tree.fb
			return missingRangeDataClassify(observation, branch)
