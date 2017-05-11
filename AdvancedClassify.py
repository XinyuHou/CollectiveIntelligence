class MatchRow:
	def __init__(self, row, allNum = False):
		if allNum:
			self.data = [float(row[i]) for i in range(len(row) - 1)]
		else:
			self.data = row[0 : len(row) - 1]

		self.match = int(row[len(row) - 1])

def loadMatch(f, allNum = False):
	rows = []
	for line in file(f):
		rows.append(MatchRow(line.split(','), allNum))

	return rows

from pylab import *
def plotAgeMatches(rows):
	xdm, ydm = [r.data[0] for r in rows if r.match == 1], \
				[r.data[1] for r in rows if r.match == 1]

	xdn, ydn = [r.data[0] for r in rows if r.match == 0], \
				[r.data[1] for r in rows if r.match == 0]

	plot(xdm, ydm, 'go')
	plot(xdn, ydn, 'ro')

	show()

def linearTrain(rows):
	averages = {}
	counts = {}

	for row in rows:
		cl = row.match

		averages.setdefault(cl, [0.0] * (len(row.data)))
		counts.setdefault(cl, 0)

		for i in range(len(row.data)):
			averages[cl][i] += float(row.data[i])

		counts[cl] += 1

	for cl, avg in averages.items():
		for i in range(len(avg)):
			avg[i] /= counts[cl]

	return averages

def dotProduct(v1, v2):
	return sum([v1[i] * v2[i] for i in range(len(v1))])

def dotProductClassify(point, avgs):
	b = (dotProduct(avgs[1], avgs[1]) - dotProduct(avgs[0], avgs[0])) / 2
	y = dotProduct(point, avgs[0]) - dotProduct(point, avgs[1]) + b

	if y > 0:
		return 0
	else:
		return 1

def yesNo(v):
	if v == 'yes':
		return 1
	elif v == 'no':
		return -1
	else:
		return 0

def matchCount(interest1, interest2):
	l1 = interest1.split(':')
	l2 = interest2.split(':')
	x = 0
	for v in l1:
		if v in l2:
			x += 1
	return x



