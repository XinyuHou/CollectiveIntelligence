import re
import math

def getWords(doc):
	splitter = re.compile('\\W*')

	words = [s.lower() for s in splitter.split(doc) if len(s) > 2 and len(s) < 20]

	return dict([(w, 1) for w in words])

def sampleTrain(cl):
	cl.train('Nobody owns the water.', 'good')
	cl.train('the quick rabbit jumps fences', 'good')
	cl.train('the quick brown fox jumps', 'good')
	cl.train('buy pharmaceuticals now', 'bad')
	cl.train('make quick money at the online casino', 'bad')

class classifier:
	def __init__(self, getFeatures, filename = None):
		self.featureCatCount = {}
		self.catCount = {}
		self.getFeatures = getFeatures
		self.thresholdes = {}

	def setThreshold(self, cat, t):
		self.thresholdes[cat] = totalItemCount

	def getThreshold(self, cat):
		if cat not in self.thresholdes:
			return 1.0

		return self.thresholdes[cat]

	def classify(self, item, default = None):
		probs = {}

		max = 0.0

		for cat in self.categories():
			probs[cat] = self.prob(item, cat)
			if probs[cat] > max:
				max = probs[cat]
				best = cat

		for cat in probs:
			if cat == best:
				continue
			if probs[cat] * self.getThreshold(best) > probs[best]:
				return default

		return best

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

class naiveBayes(classifier):
	def docProb(self, item, cat):
		features = self.getFeatures(item)

		p = 1

		for f in features:
			p *= self.weightedProb(f, cat, self.featureProb)

		return p

	def prob(self, item, cat):
		catProb = self.itemCountInCat(cat) / self.totalItemCount()
		docProb = self.docProb(item, cat)

		return docProb * catProb

class fisherClassifier(classifier):
	def __init__(self, getFeatures):
		classifier.__init__(self, getFeatures)
		self.minimums = {}

	def setMinimum(self, cat, min):
		self.minimums[cat] = min

	def getMinimum(self, cat):
		if cat not in self.minimums:
			return 0;

		return self.minimums[cat]

	def catProb(self, f, cat):
		freInThisCat = self.featureProb(f, cat)
		if freInThisCat == 0:
			return 0

		freSum = sum([self.featureProb(f, c) for c in self.categories()])

		p = freInThisCat / freSum

		return p

	def fisherProb(self, item, cat):
		p = 1
		features = self.getFeatures(item)

		for f in features:
			p *= (self.weightedProb(f, cat, self.catProb))

		fScore = -2 * math.log(p)

		return self.invChi2(fScore, len(features) * 2)

	def invChi2(self, chi, df):
		m = chi / 2.0
		print 'm: %f' % m
		sum = term = math.exp(-m)
		print 'sum&term: %f' % sum
		for i in range(1, df // 2):
			print 'i: %d' % i
			term *= m / i
			print 'term: %f' % term
			sum += term

		return min(sum, 1.0)

	def classify(self, item, default = None):
		best = default
		max = 0.0
		for c in self.categories():
			p = self.fisherProb(item, c)

			if p > self.getMinimum(c) and p > max:
				best = c
				max = p

		return best