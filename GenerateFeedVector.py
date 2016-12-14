import feedparser
import re

# Returns titile and dictionary of word counts for an RSS feed
def getWordCounts(url):
	# Parse the feed
	d = feedparser.parse(url)
	wc = {}

	# Loop over all the entries
	for e in d.entries:
		if 'summary' in e: summary = e.summary
	else: summary = e.description

	# Extract a list of words
	words = getWords(e.title + ' ' + e.summary)
	for word in words:
		wc.setdefault(word, 0)
		wc[word] += 1

	return d.feed.title, wc

def getWords(html):
	# Remove all the HTML tags
	txt = re.compile(r'<[^>]+>').sub('', html)

	# Split words
	words = re.compile(r'[^A-Z^a-z]+').split(txt)

	# Convert to lowercase
	return [word.lower() for word in words if word != '']
