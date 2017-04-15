import random
import math

people = ['Toby', 'Steve', 'Andrea', 'Sarah', 'Dave', 'Jeff', 'Fred', 'Suzie', 'Laura', 'Neil']

prefs = [('Toby', ('Steve', 'Steve')),
		('Steve', ('Suzie', 'Neil')),
		('Andrea', ('Sarah', 'Jeff')),
		('Sarah', ('Andrea', 'Laura')),
		('Dave', ('Fred', 'Andrea')),
		('Jeff', ('Toby', 'Fred')),
		('Fred', ('Laura', 'Suzie')),
		('Suzie', ('Jeff', 'Sarah')),
		('Laura', ('Andrea', 'Steve')),
		('Neil', ('Dave', 'Toby'))]

# [(1, 9), (1, 7), (1, 5), (1, 3), (1, 1)]
domain = [(1, (len(people)) - 1 - i * 2) for i in range(len(people) / 2)]

def printSolution(vec):
	peopleCopy = people[:]

	for i in range(len(vec)):
		x = int(vec[i])
		name = peopleCopy[x]

		print peopleCopy[0], peopleCopy[x]

		del peopleCopy[x]
		del peopleCopy[0]


def pairCost(vec):
	cost = 0
	peopleCopy = people[:]

	for i in range(len(vec)):
		x = int(vec[i])
		name = peopleCopy[x]

		pi1 = -1
		pi2 = -1

		for j in range(len(people)):
			if people[j] == peopleCopy[0]:
				pi1 = j
			elif people[j] == peopleCopy[x]:
				pi2 = j

		pref1 = prefs[pi1][1]
		pref2 = prefs[pi2][1]
		
		if pref1[0] == people[pi2]:
			cost += 0
		elif pref1[1] == people[pi2]:
			cost += 1
		else:
			cost += 3

		if pref2[0] == people[pi1]:
			cost += 0
		elif pref2[1] == people[pi1]:
			cost += 1
		else:
			cost += 3

		del peopleCopy[x]
		del peopleCopy[0]

	return cost