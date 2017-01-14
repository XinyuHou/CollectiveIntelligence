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

	def generateHiddenNode(self, wordIds, urls):
		
	def getAllHiddenIds(self, wordIds, urlIds):

	def setupNetwork(self, wordIds, urlIds):

	def feedForward(self):

	def getResult(self, wordIds, urlIds):
		self.setupNetwork(wordIds, urlIds)
		return self.feedForward()

	def backPropagate(self, targets, N = 0.5):

	def trainQuery(self, wordIds, urlIds, selectedUrl):
		
	def trainQueryScores(self, wordIds, urlIds, scores):

	def updateDatabase(self):
