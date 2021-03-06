from math import tanh
import sqlite3 as sqlite

def dtanh(y):
	return 1.0 - y * y

class SearchNet:
	def __init__(self, dbName, layers = 3):
		self.db = sqlite.connect(dbName)
		self.layers = layers

	def __del__(self):
		self.db.close()

	def unlockDB(self):
		self.db.close()

	def clearDB(self):
		self.db.execute('drop table HiddenNode1')
		self.db.execute('drop table HiddenNode2')
		self.db.execute('drop table Connection1')
		self.db.execute('drop table Connection2')
		self.db.execute('drop table Connection3')

	def makeTables(self):
		for layer in range(self.layers - 2):
			self.db.execute('create table HiddenNode%d(createKey)' % (layer + 1))
		
		for layer in range(self.layers - 1):
			self.db.execute('create table Connection%d(fromId, toId, strength)' % (layer + 1))

		self.db.commit()

	def getStrength(self, fromId, toId, layer):
		table = 'Connection%d' % layer

		res = self.db.execute('select strength from %s where fromId = %d and toId = %d' % (table, fromId, toId)).fetchone()
		if res == None:
			if layer == 0:
				return -0.2
			else:
				return 0

		return res[0]

	def setStrength(self, fromId, toId, layer, strength):
		table = 'Connection%d' % layer

		res = self.db.execute('select rowid from %s where fromId = %d and toId = %d' % (table, fromId, toId)).fetchone()
		if res == None:
			self.db.execute('insert into %s (fromId, toId, strength) values (%d, %d, %f)' % (table, fromId, toId, strength))
		else:
			rowid = res[0]
			self.db.execute('update %s set strength = %f where rowid = %d' % (table, strength, rowid))

	def generateHiddenNodes(self, wordIds, urls):
		if len(wordIds) > 3: return None

		# Check if we alreayd created a node for this set of words
		originalCreateKey = unicode('_'.join(sorted([str(wi) for wi in wordIds])), "utf-8")
		
		res = self.db.execute("select rowid from HiddenNode1 where createKey = '%s'" % originalCreateKey).fetchone()

		# If not, create it
		if res == None:
			print 'Create %s in HiddenNode1' % originalCreateKey
			cur = self.db.execute("insert into HiddenNode1 (createKey) values ('%s')" % originalCreateKey)
			hiddenNode1Id = cur.lastrowid

			# Put in some default weights
			# First put the weight for input and HiddenNode1
			for wordId in wordIds:
				self.setStrength(wordId, hiddenNode1Id, 1, 1.0 / len(wordIds))
			
			self.db.commit()

			# Iterate from hiddenNode1 to the last hiddenNode
			# A, B, C generate hiddenNode1 A_B_C, and hiddenNode2 A_B_C
			# Add C, E should generate hiddenNode1 C_E, and hiddenNode2 C_E, A_B_C_E
			# Add B, E should generate hiddenNode1 B_E, and hiddenNode2 B_E, B_C_E
			# Weight between node1 A_B_C and node2 A_B_C is 0.1
			# Weight between node1 C_E and node2 C_E is 0.1
			# Weight between node1 C_E and node2 A_B_C_E is 0.1 * (2 / 4) = 0.05
			# Weight between node1 B_E and node2 B_C_E is 0.1 * (2 / 3) = 0.06

			newNodesInPreviousLayer = []
			newNodesInPreviousLayer.append(originalCreateKey)
			newNodesInCurLayer = []
			for i in range(2, self.layers - 1):
				# Get all nodes from this layer
				print 'Creating HiddenNode%d and Connection%d' % (i, i)
				curNodes = [item[0] for item in self.db.execute("select * from HiddenNode%d" % i).fetchall()]
				preNodes = [item[0] for item in self.db.execute("select * from HiddenNode%d" % (i - 1)).fetchall()]

				print 'PreNode:'
				print preNodes
				print 'CurNodes'
				print curNodes
				print "NewNodesInPreviousLayer"
				print newNodesInPreviousLayer

				for preNode1 in preNodes:
					if preNode1 in newNodesInPreviousLayer:	
						preNewNode = preNode1

						if preNewNode not in curNodes: 
							# Create a new node in current layer
							cur = self.db.execute("insert into HiddenNode%d (createKey) values ('%s')" % (i, preNewNode))
							print 'Added new node in HiddenNode%d: %s' % (i, preNewNode)
							self.db.commit()

							curNodes.append(preNewNode)
							newNodesInCurLayer.append(preNewNode)

							# Add weight
							fromId = self.db.execute("select rowid from HiddenNode%d where createKey = '%s'" % (i - 1, preNewNode)).fetchone()[0]
							toId = self.db.execute("select rowid from HiddenNode%d where createKey = '%s'" % (i, preNewNode)).fetchone()[0]
							self.setStrength(fromId, toId, i, 0.1)

							# Combine each node that is not newly added in previous layer to generate new nodes
							for preNode2 in preNodes:
								if (preNode2 not in newNodesInPreviousLayer):
									preExistingNode = preNode2
									wordIds = preExistingNode.split('_')
									newWordIds = preNewNode.split('_')

									# Merge two lists without duplicates
									wordIdsSet = set(wordIds)
									newWordIdsSet = set(newWordIds)
									setDiff = newWordIdsSet - wordIdsSet
									allUniqueWordIdsSet = list(wordIdsSet) + list(setDiff)
									combinedNode = unicode('_'.join(sorted([str(wi) for wi in allUniqueWordIdsSet])), "utf-8")

									# Add combined node if not exist in current layer
									if combinedNode not in curNodes:
										print 'CurNodes'
										print curNodes
										print 'Added combinedNode node in HiddenNode%d: %s' % (i, combinedNode)
										cur = self.db.execute("insert into HiddenNode%d (createKey) values ('%s')" % (i, combinedNode))
										
										curNodes.append(combinedNode)
										newNodesInCurLayer.append(combinedNode)
										
										self.db.commit()

										# newWordsCount = len(newWordIdsSet)
										# combinedWordsCount = len(allUniqueWordIdsSet)
										# newStrength = 0.1 * (newWordsCount / combinedWordsCount)
										# print 'Set strength between %d and %d with %f in layer %d' % (fromId, toId, newStrength, i)

						# Add weights
						# Calculate the persentage of the match part and times 0.1 as new strength
						totalCurNodes = self.db.execute("select * from HiddenNode%d" % i).fetchall()
						totalPreNodes = self.db.execute("select * from HiddenNode%d" % (i -1)).fetchall()
						for preNode in totalPreNodes:
							print preNode
							fromId = self.db.execute("select rowid from HiddenNode%d where createKey = '%s'" % (i - 1, preNode[0])).fetchone()[0]
							print 'total previous nodes'
							print totalPreNodes
							print 'total current nodes'
							print totalCurNodes
							for curNodes in totalCurNodes:
								# Skip the exact matching pair, as the connection has been built in previous stage
								if preNode[0] == curNodes[0]:
									continue

								preParts = preNode[0].split('_')
								curParts = curNodes[0].split('_')
								if set(preParts).issuperset(set(curParts)):
									# Calculate the shared count
									sharedCount = set(preParts) & set(curParts)
									newStrength = 0.1 * (len(sharedCount) / float(len(preParts)))	
									
									print 'node in previous layer %s' % preNode[0]
									print 'node in current layer %s' % curNodes[0]
									print 'sharedCount: %d ' % (len(sharedCount))
									print 'preParts count: %d' % len(preParts)
					
									toId = self.db.execute("select rowid from HiddenNode%d where createKey = '%s'" % (i, curNodes[0])).fetchone()[0]
									print 'Set strength between %d and %d with %f in layer %d' % (fromId, toId, newStrength, i)
									
									self.setStrength(fromId, toId, i, newStrength)

						self.db.commit()
				
				newNodesInPreviousLayer = newNodesInCurLayer
			self.db.commit()
			# Finally put weight for last hiddenNode and output
			# A, B,  and Url1, Url2 generate weights as 
			# A_B => 0.1 => Url1
			# A_B => 0.1 => Url2
			# Newly added ndoe B_C would create weights as
			# B_C => 0.1 => Url1
			# B_C => 0.1 => Url2
			# A_B_C = 0.1 * 2 /3 => Url1
			# A_B_C = 0.1 * 2 /3 => Url2

			for node in newNodesInPreviousLayer:
				fromId = self.db.execute("select rowid from HiddenNode%d where createKey = '%s'" % (self.layers - 2, node)).fetchone()[0]
				if node == originalCreateKey:
					for url in urls:
						self.setStrength(fromId, url, self.layers - 1, 0.1)
				else:
					originalParts = originalCreateKey.split('_')
					nodeParts = node.split('_')

					if set(nodeParts).issuperset(set(originalParts)):
						# Calculate the shared count
						sharedCount = set(originalParts) & set(nodeParts)
						newStrength = 0.1 * (len(sharedCount) / float(len(nodeParts)))
						for url in urls:
							self.setStrength(fromId, url, self.layers - 1, newStrength)

			self.db.commit()

	def getAllHiddenIds(self, wordIds, urlIds):
		self.hiddenIds = []
		self.layers

		# forward
		l1 = {}
		for wordId in wordIds:
			cur = self.db.execute('select toId from Connection1 where fromId = %d' % wordId)
			for row in cur:
				l1[row[0]] = 1
		self.hiddenIds.append(l1)

		for layer in range(self.layers - 3):
			l2 = {}
			
			for hiddenId in l1.keys():
				cur = self.db.execute('select toId from Connection%d where fromId = %d' % (layer + 2, hiddenId))
				for row in cur:
					l2[row[0]] = 1
		
			self.hiddenIds.append(l2)
			l1 = l2
		print "forward result: "
		print self.hiddenIds

		# backward
		for urlId in urlIds:
			cur = self.db.execute('select fromId from Connection%d where toId = %d' % (self.layers - 1, urlId))
			for row in cur:
				self.hiddenIds[self.layers - 3][row[0]] = 1

		for layer in range(len(self.hiddenIds) - 1):
			curIndex = len(self.hiddenIds) - layer - 1
			preIndex = curIndex - 1

			for hiddenId in self.hiddenIds[curIndex].keys():
				cur = self.db.execute('select fromId from Connection%d where toId = %d' % (self.layers - layer - 2, hiddenId))
				for row in cur:
					self.hiddenIds[preIndex][row[0]] = 1
		print "forward plus backward result: "
		print self.hiddenIds

		for layer in range(len(self.hiddenIds)):
			self.hiddenIds[layer] = self.hiddenIds[layer].keys()
		print self.hiddenIds

	def setupNetwork(self, wordIds, urlIds):
		# Values
		self.wordIds = wordIds
		self.getAllHiddenIds(wordIds, urlIds)
		self.urlIds = urlIds

		# Outputs
		self.inputOut = [1.0] * len(self.wordIds)
		self.outputOut = [1.0] * len(self.urlIds)
		self.hiddenOut = []
		hiddenIdSize = len(self.hiddenIds)
		for layer in range(hiddenIdSize):
			out = [1.0] * len(self.hiddenIds[layer])
			self.hiddenOut.append(out)

		# Matrix
		self.weightMatrix = []

		# Weights between input and hidden1
		weight1 = [[self.getStrength(wordId, hiddenId, 1) for hiddenId in self.hiddenIds[0]] for wordId in self.wordIds]
		self.weightMatrix.append(weight1)

		for layer in range(hiddenIdSize - 1):
			weight = [[self.getStrength(hiddenId1, hiddenId2, layer + 2) for hiddenId2 in self.hiddenIds[layer + 1]] for hiddenId1 in self.hiddenIds[layer]]
			self.weightMatrix.append(weight)

		# Weights between last hidden to output
		weight2 = [[self.getStrength(hiddenId, urlId, self.layers - 1) for urlId in self.urlIds] for hiddenId in self.hiddenIds[hiddenIdSize - 1]]
		self.weightMatrix.append(weight2)

		print self.weightMatrix

	def feedForward(self):
		# The only inputs are the query words
		for i in range(len(self.wordIds)):
			self.inputOut[i] = 1.0

		# Between input and hidden1
		for j in range(len(self.hiddenOut[0])):
			sum = 0.0
			for i in range(len(self.wordIds)):
				sum = sum + self.inputOut[i] * self.weightMatrix[0][i][j]
			self.hiddenOut[0][j] = tanh(sum)

		# Between hidden1 and hiddenN
		for k in range(len(self.hiddenOut) - 1):

			for j in range(len(self.hiddenOut[k + 1])):
				sum = 0.0
				for i in range(len(self.hiddenOut[k])):
					sum = sum + self.hiddenOut[k][i] * self.weightMatrix[k + 1][i][j]
				self.hiddenOut[k + 1][j] = tanh(sum)

		# Between hiddenN and output
		for k in range(len(self.urlIds)):
			sum = 0.0
			hiddenOutSize = len(self.hiddenOut)
			weightMatrixSize = len(self.weightMatrix)
			for j in range(len(self.hiddenOut[hiddenOutSize - 1])):
				sum = sum + self.hiddenOut[hiddenOutSize - 1][j] * self.weightMatrix[weightMatrixSize - 1][j][k]

			self.outputOut[k] = tanh(sum)

		return self.outputOut[:]

	def getResult(self, wordIds, urlIds):
		self.setupNetwork(wordIds, urlIds)
		return self.feedForward()

	def dtanh(y):
		return 1.0 - y * y

	def backPropagate(self, targets, N = 0.5):
		# Calculate errors for output
		outputDeltas = [0.0] * len(self.urlIds)

		for k in range(len(self.urlIds)):
			error = targets[k] - self.outputOut[k]
			outputDeltas[k] = dtanh(self.outputOut[k]) * error

		# Calculate errors for hiddenN
		hiddenIdsSize = len(self.hiddenIds)
		weightMatrixSize = len(self.weightMatrix)
		hiddenOutSize = len(self.hiddenOut)
		hiddenDeltas = [0.0] * len(self.hiddenIds[hiddenIdsSize - 1])

		for j in range(len(self.hiddenIds[hiddenIdsSize - 1])):
			error = 0
			for k in range(len(self.urlIds)):
				error = error + outputDeltas[k] * self.weightMatrix[weightMatrixSize - 1][j][k]
			hiddenDeltas[j] = dtanh(self.hiddenOut[hiddenOutSize - 1][j] * error)

		# Update output weights
		for j in range(len(self.hiddenIds[hiddenIdsSize - 1])):
			for k in range(len(self.urlIds)):
				change = outputDeltas[k] * self.hiddenOut[hiddenOutSize - 1][j]
				self.weightMatrix[weightMatrixSize - 1][j][k] = self.weightMatrix[weightMatrixSize - 1][j][k] + N * change

		# Do the same thing forward to update the rest of the weight matrix
		# Bewteen hidden1 and hiddenN
		for i in range(hiddenIdsSize - 2, 0, -1):
			nextHiddenDeltas = [0.0] * len(self.hiddenIds[i - 1])
			for j in range(len(self.hiddenIds[i - 1])):
				error = 0
				for k in range(len(self.hiddenIds[i])):
					error = error + hiddenDeltas[k] * self.weightMatrix[i][j][k]
				nextHiddenDeltas[j] = dtanh(self.hiddenOut[i - 1][j] * error)

			for j in range(len(self.hiddenIds[i - 1])):
				for k in range(len(self.hiddenIds[i])):
					change = hiddenDeltas[k] * self.hiddenOut[i - 1][j]
					self.weightMatrix[i][j][k] = self.weightMatrix[i][j][k] + N * change

			hiddenDeltas = nextHiddenDeltas

		# Between input and hidden1
		for i in range(len(self.wordIds)):
			for j in range(len(self.hiddenIds[0])):
				change = hiddenDeltas[j] * self.inputOut[i]
				self.weightMatrix[0][i][j] = self.weightMatrix[0][i][j] + N * change

	def trainQuery(self, wordIds, urlIds, selectedUrl):
		# Generate a hidden node if necessary
		self.generateHiddenNodes(wordIds, urlIds)

		self.setupNetwork(wordIds, urlIds)
		self.feedForward()
		targets = [0.0] * len(urlIds)
		targets[urlIds.index(selectedUrl)] = 1.0
		self.backPropagate(targets)
		self.updateDatabase()

	def updateDatabase(self):
		# Set them to database values
		hiddenIdsSize = len(self.hiddenIds)
		weightMatrixSize = len(self.weightMatrix)

		for i in range(len(self.wordIds)):
			for j in range(len(self.hiddenIds[0])):
				self.setStrength(self.wordIds[i], self.hiddenIds[0][j], 1, self.weightMatrix[0][i][j])

		for i in range(hiddenIdsSize - 1):
			for j in range(len(self.hiddenIds[i + 1])):
				for k in range(len(self.hiddenIds[i])):
					
					self.setStrength(self.hiddenIds[i][k], self.hiddenIds[i + 1][j], i + 2, self.weightMatrix[i + 1][k][j])

		for j in range(len(self.hiddenIds)):
			for k in range(len(self.urlIds)):
				self.setStrength(self.hiddenIds[hiddenIdsSize - 1][j], self.urlIds[k], self.layers - 1, self.weightMatrix[weightMatrixSize - 1][j][k])

		self.db.commit()
