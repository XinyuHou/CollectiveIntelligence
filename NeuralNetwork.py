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
		