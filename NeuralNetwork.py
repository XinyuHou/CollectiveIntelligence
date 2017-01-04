from math import tanh
import sqlite3 as sqlite

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

		res = self.db.execute('select strength from %s where fromId = %d amd toId = %d' % (table, fromId, toId)).fetchone()
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