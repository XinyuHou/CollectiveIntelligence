from random import random, randint, choice
from copy import deepcopy
from math import log

class FuncWrapper:
	def __init__(self, function, childCount, name):
		self.function = function
		self.childCount = childCount
		self.name = name

class Node:
	def __init__(self, fw, children):
		self.function = fw.function
		self.name = fw.name
		self.children = children

	def evaluate(self, inp):
		results = [n.evaluate(inp) for n in self.children]
		return self.function(results)

class ParamNode:
	def __init__(self, idx):
		self.idx = idx

	def evaluate(self, inp):
		return inp[self.idx]

class ConstNode:
	def __init__(self, v):
		self.v = v

	def evaluate(self, inp):
		return self.v

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
