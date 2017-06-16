from random import random, randint, choice
from copy import deepcopy
from math import log

class FuncWrapper():
	def __init__(self, function, childCount, name):
		self.function = function
		self.childCount = childCount
		self.name = name

class Node():
	def __init__(self, fw, children):
		self.function = fw.function
		self.name = fw.name
		self.children = children

	def evaluate(self, inp):
		results = [n.evaluate(inp) for n in self.children]
		return self.function(results)

	def display(self, indent = 0):
		print ('%s%s' % ('  ' * indent, self.name))
		for c in self.children:
			c.display(indent + 1)

class ParamNode():
	def __init__(self, idx):
		self.idx = idx

	def evaluate(self, inp):
		return inp[self.idx]

	def display(self, indent = 0):
		print ('%sp%d' % ('  ' * indent, self.idx))

class ConstNode():
	def __init__(self, v):
		self.v = v

	def evaluate(self, inp):
		return self.v

	def display(self, indent = 0):
		print ('%s%d' % ('  ' * indent, self.v))

addw = FuncWrapper(lambda l : l[0] + l[1], 2, 'add')
subw = FuncWrapper(lambda l : l[0] - l[1], 2, 'subtract')
mulw = FuncWrapper(lambda l : l[0] * l[1], 2, 'multiply')

def ifFunc(l):
	if l[0] > 0:
		return l[1]
	else:
		return l[2]
ifw = FuncWrapper(ifFunc, 3, 'if')

def isGreater(l):
	if l[0] > l[1]:
		return 1
	else:
		return 0
gtw = FuncWrapper(isGreater, 2, 'isgreater')

fList = [addw, mulw, ifw, gtw, subw]

def exampleTree():
	return Node(ifw, [
			Node(gtw, [ParamNode(0), ConstNode(3)]),
			Node(addw, [ParamNode(1), ConstNode(5)]),
			Node(subw, [ParamNode(1), ConstNode(2)]),
		])

def makeRandomTree(pc, maxDepth = 4, fpr = 0.5, ppr = 0.6):
	if random() < fpr and maxDepth > 0:
		f = choice(fList)
		children = [makeRandomTree(pc, maxDepth - 1, fpr, ppr) for i in range(f.childCount)]

		return Node(f, children)

	elif random() < ppr:
		return ParamNode(randint(0, pc - 1))
	else:
		return ConstNode(randint(0, 10))

def hiddenFunction(x, y):
	return x ** 2 + 2 * y + 3 * x + 5

def buildHiddenSet():
	rows = []
	for i in range(200):
		x = randint(0, 40)
		y = randint(0, 40)
		rows.append([x, y, hiddenFunction(x, y)])
	return rows

def scoreFunction(tree, s):
	dif = 0
	for data in s:
		v = tree.evaluate([data[0], data[1]])
		dif += abs(v - data[2])
	return dif

def mutate(t, pc, prob = 0.1):
	if random() < prob:
		return makeRandomTree(pc)
	else:
		result = deepcopy(t)
		if isinstance(t, Node):
			result.children = [mutate(c, pc, prob) for c in t.children]
		return result

def crossover(t1, t2, prob = 0.7, top = 1):
	r = random()
	if r < prob and not top:
		return deepcopy(t2)
	else:
		result = deepcopy(t1)
		if hasattr(t1,'children') and hasattr(t2,'children'):
			result.children = [crossover(c, choice(t2.children), prob, 0) for c in t1.children]

		return result

def getRankFunction(dataset):
	def rankFunction(population):
		scores = [(scoreFunction(t, dataset), t) for t in population]
		#print (scores)
		#sorted(scores, key=operator.itemgetter(0))
		scores.sort(key=lambda x: x[0])
		return scores
	return rankFunction

def evolve(pc, popSize, rankFunction, maxGen = 500, mutationRate = 0.1, breedingRate = 0.4, pExp = 0.7, pNew = 0.05):
	def selectIndex():
		return int(log(random()) / log(pExp)) % popSize

	population = [makeRandomTree(pc) for i in range(popSize)]
	for i in range(maxGen):
		scores = rankFunction(population)
		print (scores[0][0])
		if scores[0][0] == 0:
			break

		newPop = [scores[0][1], scores[1][1]]

		while len(newPop) < popSize:
			if random() > pNew:
				newPop.append(mutate(
								crossover(scores[selectIndex()][1],
											scores[selectIndex()][1],
											prob = breedingRate),
											pc, prob = mutationRate))
			else:
				newPop.append(makeRandomTree(pc))
		
		population = newPop
	scores[0][1].display()
	return scores[0][1]
