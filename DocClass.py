import re
import math

def getWords(doc):
	splitter = re.compile('\\W*')

	words = [s.lower() for s in splitter.split(doc) if len(s) > 2 and len(s) < 20]

	return dict([(w, 1) for w in words])

class classifier:
	def __init__(self, getFeatures, filename = None):
		self.featureCatCount = {}
		self.catCount = {}
		self.getFeatures = getFeatures

	def incFeatureCatCount(self, f, cat):
		self.featureCatCount.setdefault(f, {})
		self.featureCatCount[f].setdefault(cat, 0)
		self.featureCatCount[f][cat] += 1

	def incCatCount(self, cat):
		self.catCount.setdefault(cat, 0)
		self.catCount[cat] += 1

	def featureCount(self, f, cat):
		if f in self.featureCatCount and cat in self.featureCatCount[f]:
			return float(self.featureCatCount[f][cat])
		return 0.0

	def itemCountInCat(self, cat):
		if cat in self.catCount:
			return float(self.catCount[cat])
		return 0

	def totalItemCount(self):
		return sum(self.catCount.values())

	def categories(self):
		return self.catCount.keys()

	def train(self, item, cat):
		features = self.getFeatures(item)

		for f in features:
			self.incFeatureCatCount(f, cat)

		self.incCatCount(cat)

	def featureProb(self, f, cat):
		if self.itemCountInCat(cat) == 0:
			return 0

		return self.featureCount(f, cat) / self.itemCountInCat(cat)

	def weightedProb(self, f, cat, prf, weight = 1.0, assumedProb = 0.5):
		basicProb = prf(f, cat)

		total = sum([self.featureCount(f, c) for c in self.categories()])

		# a weight of 1 means the assumed probability is weighted the same as one word
		# (weight * assumedProb) => the assumed appear time in this cat
		# (total * basicProb) => the average appear time in this cat
		# (weight + total) => total appear time
		bp = ((weight * assumedProb) + (total * basicProb)) / (weight + total)
		return bp

def sampleTrain(cl):
	cl.train('Nobody owns the water.', 'good')
	cl.train('the quick rabbit jumps fences', 'good')
	cl.train('the quick brown fox jumps', 'good')
	cl.train('buy pharmaceuticals now', 'bad')
	cl.train('make quick money at the online casino', 'bad')
