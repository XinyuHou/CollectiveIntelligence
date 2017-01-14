from math import tanh
import sqlite3 as sqlite

def dtanh(y):
	return 1.0 - y * y

class SearchNet:
	def __init__(self, dbName):
		self.db = sqlite.connect(dbName)

	def __del__(self):
		self.db.close()

	def makeTables(self):
		self.db.execute('create table HiddenNode(createKey)')
		self.db.execute('create table WordHidden(fromId, toId, strength)')
		self.db.execute('create table HiddenUrl(fromId, toId, strength)')

		self.db.commit()

	def getStrength(self, fromId, toId, layer):
		if layer == 0:
			table = 'WordHidden'
		else:
			table = 'HiddenUrl'

		res = self.db.execute('select strength from %s where fromId = %d and toId = %d' % (table, fromId, toId)).fetchone()
		if res == None:
			if layer == 0: return -0.2
			if layer == 1: return 0

		return res[0]

	def setStrength(self, fromId, toId, layer, strength):
		if layer == 0:
			table = 'WordHidden'
		else:
			table = 'HiddenUrl'

		res = self.db.execute('select rowid from %s where fromId = %d and toId = %d' % (table, fromId, toId)).fetchone()
		if res == None:
			self.db.execute('insert into %s (fromId, toId, strength) values (%d, %d, %f)' % (table, fromId, toId, strength))
		else:
			rowid = res[0]
			self.db.execute('update %s set strength = %f where rowid = %d' % (table, strength, rowid))

	def generateHiddenNode(self, wordIds, urls):
		if len(wordIds) > 3: return None

		# Check if we alreayd created a node for this set of words
		createKey = '_'.join(sorted([str(wi) for wi in wordIds]))
		
		res = self.db.execute("select rowid from HiddenNode where createKey = '%s'" % createKey).fetchone()

		# If not, create it
		if res == None:
			cur = self.db.execute("insert into HiddenNode (createKey) values ('%s')" % createKey)
			hiddenId = cur.lastrowid

			# Put in some default weights
			for wordId in wordIds:
				self.setStrength(wordId, hiddenId, 0, 1.0 / len(wordIds))
			
			for urlId in urls:
				self.setStrength(hiddenId, urlId, 1, 0.1)

			self.db.commit()

	def getAllHiddenIds(self, wordIds, urlIds):
		l1 = {}
		for wordId in wordIds:
			cur = self.db.execute('select toId from WordHidden where fromId = %d' % wordId)
			for row in cur:
				l1[row[0]] = 1

		for urlId in urlIds:
			cur = self.db.execute('select fromId from HiddenUrl where toId = %d' % urlId)
			for row in cur:
				l1[row[0]] = 1

		return l1.keys()

	def setupNetwork(self, wordIds, urlIds):
		# Value lists
		self.wordIds = wordIds
		self.hiddenIds = self.getAllHiddenIds(wordIds, urlIds)
		self.urlIds = urlIds

		# Node outputs
		self.aInput = [1.0] * len(self.wordIds)
		self.aHidden = [1.0] * len(self.hiddenIds)
		self.aOutput = [1.0] * len(self.urlIds)

		print self.aInput
		print self.aHidden
		print self.aOutput

		# Create weights matrix
		self.weightInput = [[self.getStrength(wordId, hiddenId, 0) for hiddenId in self.hiddenIds] for wordId in self.wordIds]
		self.weightOutput = [[self.getStrength(hiddenId, urlId, 1) for urlId in self.urlIds] for hiddenId in self.hiddenIds]

		print self.weightInput
		print self.weightOutput

	def feedForward(self):
		# The only inputs are the query words
		for i in range(len(self.wordIds)):
			self.aInput[i] = 1.0

		# Hidden activations
		for j in range(len(self.hiddenIds)):
			sum = 0.0
			for i in range(len(self.wordIds)):
				sum = sum + self.aInput[i] * self.weightInput[i][j]

			self.aHidden[j] = tanh(sum)

		print self.aHidden

		# Output activations
		for k in range(len(self.urlIds)):
			sum = 0.0
			for j in range(len(self.hiddenIds)):
				sum = sum + self.aHidden[j] * self.weightOutput[j][k]

			self.aOutput[k] = tanh(sum)

		print self.aOutput

		return self.aOutput[:]

	def getResult(self, wordIds, urlIds):
		self.setupNetwork(wordIds, urlIds)
		return self.feedForward()

	def backPropagate(self, targets, N = 0.5):
		# Calculate errors for output
		outputDeltas = [0.0] * len(self.urlIds)

		for k in range(len(self.urlIds)):
			error = targets[k] - self.aOutput[k]
			outputDeltas[k] = dtanh(self.aOutput[k]) * error

		# Calculate errors for hidden layer
		hiddenDeltas = [0.0] * len(self.hiddenIds)

		for j in range(len(self.hiddenIds)):
			error = 0
			for k in range(len(self.urlIds)):
				error = error + outputDeltas[k] * self.weightOutput[j][k]
			hiddenDeltas[j] = dtanh(self.aHidden[j] * error)

		# Update output weights
		for j in range(len(self.hiddenIds)):
			for k in range(len(self.urlIds)):
				change = outputDeltas[k] * self.aHidden[j]
				self.weightOutput[j][k] = self.weightOutput[j][k] + N * change

		# Update input weights
		for i in range(len(self.wordIds)):
			for j in range(len(self.hiddenIds)):
				change = hiddenDeltas[j] * self.aInput[i]
				self.weightInput[i][j] = self.weightInput[i][j] + N * change

	def trainQuery(self, wordIds, urlIds, selectedUrl):
		# Generate a hidden node if necessary
		self.generateHiddenNode(wordIds, urlIds)

		self.setupNetwork(wordIds, urlIds)
		self.feedForward()
		targets = [0.0] * len(urlIds)
		targets[urlIds.index(selectedUrl)] = 1.0
		self.backPropagate(targets)
		self.updateDatabase()

	def trainQueryScores(self, wordIds, urlIds, scores):
		# Generate a hidden node if necessary
		self.generateHiddenNode(wordIds, urlIds)

		self.setupNetwork(wordIds, urlIds)
		self.feedForward()
		targets = [0.0] * len(urlIds)
		for index, target in enumerate(targets):
			targets[index] = scores[index]
		self.backPropagate(targets)
		self.updateDatabase()

	def updateDatabase(self):
		# Set them to database values
		for i in range(len(self.wordIds)):
			for j in range(len(self.hiddenIds)):
				self.setStrength(self.wordIds[i], self.hiddenIds[j], 0, self.weightInput[i][j])

		for j in range(len(self.hiddenIds)):
			for k in range(len(self.urlIds)):
				self.setStrength(self.hiddenIds[j], self.urlIds[k], 1, self.weightOutput[j][k])

		self.db.commit()
