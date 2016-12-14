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

	return getattr(d.feed, 'title', 'Unknown title'), wc

def getWords(html):
	# Remove all the HTML tags
	txt = re.compile(r'<[^>]+>').sub('', html)

	# Split words
	words = re.compile(r'[^A-Z^a-z]+').split(txt)

	# Convert to lowercase
	return [word.lower() for word in words if word != '']


# Loop through feedlist.txt to generate the word count table
apcount = {}
wordCounts = {}
feedList = []
n = 1
for feedUrl in file('Feedlist.txt'):
	feedList.append(feedUrl)
	print 'parsing {} url'.format(n)
	
	title, wc = getWordCounts(feedUrl)
	n += 1
	wordCounts[title] = wc
	for word, count in wc.items():
		apcount.setdefault(word, 0)
		if count > 1:
			apcount[word] += 1

# only count the word that appears between 10% and 50% of all the blogs
wordList = []
for w, appearCount in apcount.items():
	frac = float(appearCount) / len(feedList)
	if frac > 0.1 and frac < 0.5:
		wordList.append(w)

# out put the result into a file
out = file('BlogData.txt', 'w')
out.write('Blog')
for word in wordList:
	out.write('\t%s' % word)
out.write('\n')
for blog, wc in wordCounts.items():
	# Deal with the unicode outside of the ascii range
	blog = blog.encode('ascii', 'ignore')
	out.write(blog)
	for word in wordList:
		if word in wc:
			out.write('\t%d' % wc[word])
		else:
			out.write('\t0')
	out.write('\n')
