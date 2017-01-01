import re
import urllib2
import sqlite3 as sqlite
from bs4 import BeautifulSoup
from urlparse import urljoin

# A list of words to ignore
ignoreWords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])

class Crawler:
	def __init__(self, dbName):
		self.db = sqlite.connect(dbName)

	def __del__(self):
		self.db.close()

	def dbCommit(self):
		self.db.commit()

	#Auxilliary function for getting an entry id and adding it if ti's not present
	def getEntryId(self, table, field, value, createNew = True):
		return None

	# Index an individual page
	def addToIndex(self, url, soup):
		print 'Indexing %s' % url

	# Extract the text from an HTML page (no tags)
	def getTextOnly(self, soup):
		str = soup.string

		if str == None:
			c = soup.contents
			resultText = ''

			for t in c:
				subText = self.getTextOnly(t)
				resultText += subText + '\n'

			return resultText

		else:
			return v.strip()

	# Separate the words by any non-whitespace character
	def separateWords(self, text):
		splitter = re.compile('\\W*')
		return [s.lower() for s in splitter.split(text) if s != '']

	# Return true if this url is already indexed
	def isIndexed(self, url):
		return False

	# Add a link between two pages
	def addLinkRef(self, urlFrom, urlTo, linkText):
		pass

	# Starting with a list of pages, do a breadth first search to the given depth, indexing pages as we go
	def crawl(self, pages, depth = 2):
		pass

	# Create the database tables
	def createIndexTables(self):
		pass

	# Crawl pages
	def crawl(self, pages, depth = 1):
		# breadth first search
		for i in range(depth):
			newPages = set()
			for page in pages:
				try:
					c = urllib2.urlopen(page)
				except:
					print "Could not open %s" % page
					continue
				soup = BeautifulSoup(c.read())
				self.addToIndex(page, soup)

				links = soup('a')
				for link in links:
					if ('href' in dict(link.attrs)):
						print 'link hrep: ' + link['href']
						url = urljoin(page, link['href'])
						print 'url: ' + url

						if url.find("'") != -1: continue

						# Remove location part
						url = url.split('#')[0]
						print 'url without location: ' + url

						if url[0:4] == 'http' and not self.isIndexed(url):
							newPages.add(url)

						linkText = self.getTextOnly(link)
						#print 'link text: ' + linkText

						self.addLinkRef(page, url, linkText)
						print '=========='

				self.dbCommit()

			pages = newPages


	# Prepare data base table
	def createIndexTables(self):
		self.db.execute('create table UrlList(url)')
		self.db.execute('create table WordList(word)')
		self.db.execute('create table WordLocation(urlId, wordId, location)')
		self.db.execute('create table link(fromId integer, toId integer)')
		self.db.execute('create table LinkWords(wordId, linkId)')

		self.db.execute('create index WordIndex on WordList(word)')
		self.db.execute('create index UrlIndex on UrlList(url)')
		self.db.execute('create index WordUrlIndex on WordLocation(wordId)')
		self.db.execute('create index UrlToIndex on link(toId)')
		self.db.execute('create index UrlFromIndex on link(fromId)')

		self.dbCommit()
