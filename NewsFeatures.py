import feedparser
import re

feedList = ['http://today.reuters.com/rss/topNews',
        	'http://today.reuters.com/rss/domesticNews',
        	'http://today.reuters.com/rss/worldNews',
        	'http://hosted.ap.org/lineups/TOPHEADS-rss_2.0.xml',
        	'http://hosted.ap.org/lineups/USHEADS-rss_2.0.xml',
        	'http://hosted.ap.org/lineups/WORLDHEADS-rss_2.0.xml',
        	'http://hosted.ap.org/lineups/POLITICSHEADS-rss_2.0.xml',
        	'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        	'http://www.nytimes.com/services/xml/rss/nyt/International.xml',
        	'http://news.google.com/?output=rss',
        	'http://feeds.salon.com/salon/news',
        	'http://www.foxnews.com/xmlfeed/rss/0,4313,0,00.rss',
        	'http://www.foxnews.com/xmlfeed/rss/0,4313,80,00.rss',
        	'http://www.foxnews.com/xmlfeed/rss/0,4313,81,00.rss',
        	'http://rss.cnn.com/rss/edition.rss',
        	'http://rss.cnn.com/rss/edition_world.rss',
        	'http://rss.cnn.com/rss/edition_us.rss']

def stripHTML(h):
	p = ''
	s = 0
	for c in h:
		if c == '<':
			s = 1
		elif c == '>':
			s = 0
			p += ' '
		elif s == 0:
			p += c
	return p

def separateWords(text):
	splitter = re.compile('\\W*')
	return [s.lower() for s in splitter.split(text) if len(s) > 3]

def getArticleWords():
	allWords = {}
	articleWords = []
	articleTitles = []
	ec = 0

	for feed in feedList:
		f = feedparser.parse(feed)

		for e in f.entries:
			if e.title in articleTitles:
				continue
			

			txt = e.title.encode('utf8')
			if 'summary' in e: 
				summary = e.summary
			elif 'description' in e:
				summary = e.description
			txt += stripHTML(summary.encode('utf8'))

			words = separateWords(txt)
			articleWords.append({})
			articleTitles.append(e.title)

			for word in words:
				allWords.setdefault(word, 0)
				allWords[word] += 1
				articleWords[ec].setdefault(word, 0)
				articleWords[ec][word] += 1

			ec += 1

	return allWords, articleWords, articleTitles

def makeMatrix(allw, articleWords):
	wordVec = []

	for w, c in allw.items():
		if c > 3 and c < len(articleWords) * 0.6:
			wordVec.append(w)
	l1 = [[(word in f and f[word] or 0) for word in wordVec] for f in articleWords]

	return l1, wordVec

from numpy import *
def showFeatures(w, h, titles, wordVec, out = 'Features.txt'):
	outFile = file(out, 'w')
	pc, wc = shape(h)

	topPatterns = [[] for i in range(len(titles))]
	patternNames = []

	for i in range(pc):
		slist = []

		for j in range(wc):
			slist.append((h[i,j], wordVec[j]))

		slist.sort()
		slist.reverse()

		n = [s[1] for s in slist[0 : 6]]
		outFile.write(str(n) + '\n')
		patternNames.append(n)

		flist = []
		for j in range(len(titles)):
			flist.append((w[j,i], titles[j]))
			topPatterns[j].append((w[j,i], i, titles[j]))

		flist.sort()
		flist.reverse()

		for f in flist[0 : 3]:
			outFile.write(str(f) + '\n')

		outFile.write('\n')

	outFile.close()

	return topPatterns, patternNames

def showArticles(titles, topPatterns, patternNames, out = 'Articles.txt'):
	outFile = file(out, 'w')

	for j in range(len(titles)):
		outFile.write(titles[j].encode('utf-8') + '\n')

		topPatterns[j].sort()
		topPatterns[j].reverse()

		for i in range(3):
			outFile.write(str(topPatterns[j][i][0]) + ' ' + str(patternNames[topPatterns[j][i][1]]) + '\n')

		outFile.write('\n')

	outFile.close()



