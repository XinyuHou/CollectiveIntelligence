import NMF
import urllib2
from numpy import *

tickers = ['YHOO', 'AVP', 'BIIB', 'BP', 'CL', 'CVX', 'DNA', 'EXPE', 'GOOG', 'PG', 'XOM', 'AMGN']

shortest = 300
prices = {}
dates = None

for t in tickers:
	# TOOD fix out of date yahoo url
	url = 'http://ichart.finance.yahoo.com/table.csv?' + \
							's=%s&d=11&e=26&f=2006&g=d&a=3&b=12&c=1996' % t +\
							'&ignore=.csv'
	print url
	rows = urllib2.urlopen(url).readlines()

	prices[t] = [float(r.split(',')[5]) for r in rows[1 :] if r.strip() != '']
	if len(prices[t]) < shortest:
		shortest = len(prices[t])

	if not dates:
		dates = [r.split(',')[0] for r in rows[1 :] if r.strip() != '']

l1 = [[prices[tickers[i]][j] for i in range(len(tickers))] for j in range(shortest)]

w, h = NMF.factorize(matrix(l1), pc = 5)

print h
print w
