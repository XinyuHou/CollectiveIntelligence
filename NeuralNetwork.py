from math import tanh
import sqlite3 as sqlite

class SearchNet:
	def __init__(self, dbName):
		self.db = sqlite.connect(dbName)

	def __del__(self):
		self.db.close()

	def makeTables(self):
		self.db.execute('create table HiddenNode(create_key)')
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

		res = self.db.execute('select rowid from %s where fromId = %d amd toId = %d' % (table, fromId, toId)).fetchone()
		if res == None:
			self.db.execute('insert into %s (fromId, toId, strength) values (%d, %d, %f)' % (table, fromId, toId, strength))
		else:
			rowid = res[0]
			self.db.execute('update %s set strength = %f where rowid = %d' % (table, strength, rowid))
	