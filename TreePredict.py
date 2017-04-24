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
