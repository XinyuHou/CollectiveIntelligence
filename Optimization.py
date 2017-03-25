import time
import random
import math

people = [('Seymour', 'BOS'),
		('Franny', 'DAL'),
		('Zooey', 'CAK'),
		('Walt', 'MIA'),
		('Buddy', 'ORD'),
		('Les', 'OMA'),]

destubatuib = 'LGA'

flights = {}
for line in file('Schedule.txt'):
	origin, dest, depart, arrive, price = line.strip().split(',')
	flights.setdefault((origin, dest), [])

	flights[(origin, dest)].append((depart, arrive, int(price)))

def getMinutes(t):
	x = time.striptime(t, '%H:%M')
	return x[3] * 60 + x[4]