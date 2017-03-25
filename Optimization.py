import time
import random
import math

people = [('Seymour', 'BOS'),
		('Franny', 'DAL'),
		('Zooey', 'CAK'),
		('Walt', 'MIA'),
		('Buddy', 'ORD'),
		('Les', 'OMA'),]

destination = 'LGA'

flights = {}
for line in file('Schedule.txt'):
	origin, dest, depart, arrive, price = line.strip().split(',')
	flights.setdefault((origin, dest), [])

	flights[(origin, dest)].append((depart, arrive, int(price)))

def getMinutes(t):
	x = time.strptime(t, '%H:%M')
	return x[3] * 60 + x[4]

def printSchedule(r):
	for d in range(len(r) / 2):
		name = people[d][0]
		origin = people[d][1]
		out = flights[(origin, destination)][r[2 * d]]
		ret = flights[(origin, destination)][r[2 * d + 1]]

		print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin,
														out[0], out[1], out[2],
														ret[0], ret[1], ret[2])

def scheduleCost(sol):
	totalPrice = 0
	latestArrival = 0
	earliestDep = 24 * 60

	for d in range(len(sol) / 2):
		# Get the inbound and outbound flights
		origin = people[d][1]
		outbound = flights[(origin, destination)][int(sol[2 * d])]
		returnf = flights[(origin, destination)][int(sol[2 * d + 1])]

		# Total price is the price of tall outbound and return flights
		totalPrice += outbound[2]
		totalPrice += returnf[2]

		# Track the latest arrival tand the earliest departure
		if latestArrival < getMinutes(outbound[1]):
			latestArrival = getMinutes(outbound[1])
		if earliestDep > getMinutes(returnf[0]):
			earliestDep = getMinutes(returnf[0])

	# Every person must wait at the airport until the latest person arrives.
	# They also must arrive at the same time and wait for their flights.
	totalWait = 0
	for d in range(len(sol) / 2):
		origin = people[d][1]
		outbound = flights[(origin, destination)][int(sol[2 * d])]
		returnf = flights[(origin, destination)][int(sol[2 * d + 1])]
		totalWait += latestArrival - getMinutes(outbound[1])
		totalWait += getMinutes(returnf[0]) - earliestDep

	# Does this solution require an extra day of car rental? extra $50
	if latestArrival < earliestDep:
		totalPrice += 50

	return totalPrice + totalWait

