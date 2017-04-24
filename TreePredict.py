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

