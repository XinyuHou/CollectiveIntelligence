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
		out = flights[(origin, destination)][int(r[2 * d])]
		ret = flights[(origin, destination)][int(r[2 * d + 1])]

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
		outDepTime = outbound[0]
		returnDepTime = returnf[0]
		outFlightTime = getMinutes(outbound[1]) - getMinutes(outbound[0])
		returnFlightTime = getMinutes(returnf[1]) - getMinutes(returnf[0])

		# Total price is the price of tall outbound and return flights
		totalPrice += outbound[2]
		totalPrice += returnf[2]
		totalPrice += outFlightTime * 0.5;
		totalPrice += returnFlightTime * 0.5;

		eightAM = getMinutes('8:00')
		if getMinutes(outDepTime) < eightAM:
			totalPrice += 20

		if getMinutes(returnDepTime) < eightAM:
			totalPrice += 20

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

def randomOptimize(domain, costf):
	best = 99999999
	bestr = None

	for i in range(1000):
		r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

		cost = costf(r)

		if cost < best:
			best = cost
			bestr = r

	return bestr

def hillClimb(domain, costf):
	sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

	while 1:
		neighbors=[]

		for j in range(len(domain)):
			if sol[j] > domain[j][0]:
				neighbors.append(sol[0 : j] + [sol[j] - 1] + sol[j + 1 :])
			if sol[j] < domain[j][0]:
				neighbors.append(sol[0 : j] + [sol[j] + 1] + sol[j + 1 :])

		current = costf(sol)
		best = current

		for j in range(len(neighbors)):
			cost = costf(neighbors[j])
			if cost < best:
				best = cost
				sol = neighbors[j]

		if best == current:
			break

	return sol

def randomStartPointsAnnealing(domain, costf, random_times = 3):
	sol = []
	bestSolScore = 99999999;
	for i in range(random_times):
		s = annealingOptimize(domain, costf)
		score = scheduleCost(s)
		if (bestSolScore > score):
			bestSolScore = score
			sol = s

	return sol

def annealingOptimize(domain, costf, T = 10000.0, cool = 0.95, step = 1):
	# Initialize the values randomly
	vec = [float(random.randint(domain[i][0], domain[i][1])) for i in range(len(domain))]

	while T > 0.1:
		# Choose one of the indices
		i = random.randint(0, len(domain) - 1)

		# Choose a direction to change it
		dir = step * (-1) ** int(round(random.random()))

		# New list with one of the values changed
		vecb = vec[:]
		vecb[i] += dir
		if vecb[i] < domain[i][0]:
			vecb[i] = domain[i][0]
		elif vecb[i] > domain[i][1]:
			vecb[i] = domain[i][1]

		# Calculate the current cost and the new cost
		cc = costf(vec)
		nc = costf(vecb)

		if nc < cc:
			vec = vecb
		else:
			p = pow(math.e, (-nc - cc) / T)
			if random.random() < p:
				vec = vecb

		# Decrease the temperature
		T = T * cool

	return vec

def geneticOptimize(domain, costf, popSize = 50, step = 1, mutPorb = 0.2, elite = 0.2, maxIter = 100):
	# Mutation
	def mutate(vec):
		i = random.randint(0, len(domain) - 1)
		if random.random() < 0.5 and vec[i] > domain[i][0]:
			return vec[0 : i] + [vec[i] - step] + vec[i + 1 :]
		elif vec[i] < domain[i][1]:
			return vec[0 : i] + [vec[i] + step] + vec[i + 1 :]
		return vec

	# Crossover
	def crossover(r1, r2):
		i = random.randint(1, len(domain) - 2)

		return r1[0 : i] + r2[i :]

	# Initial population
	pop = []
	for i in range(popSize):
		vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
		pop.append(vec)

	topElite = int(elite * popSize)

	for i in range(maxIter):
		scores = [(costf(v), v) for v in pop]
		scores.sort()
		ranked = [v for (s, v) in scores]

		pop = ranked[0 : topElite]

		while len(pop) < popSize:
			if random.random() < mutPorb:
				c = random.randint(0, topElite)
				pop.append(mutate(ranked[c]))
			else:
				c1 = random.randint(0, topElite)
				c2 = random.randint(0, topElite)
				pop.append(crossover(ranked[c1], ranked[c2]))
		print scores[0][0]

	return scores[0][1]

def improvedGeneticOptimize(domain, costf, popSize = 50, step = 1, mutPorb = 0.2, elite = 0.2, maxIter = 100, maxNoImproveIter = 10):
	# Mutation
	def mutate(vec):
		i = random.randint(0, len(domain) - 1)
		if random.random() < 0.5 and vec[i] > domain[i][0]:
			return vec[0 : i] + [vec[i] - step] + vec[i + 1 :]
		elif vec[i] < domain[i][1]:
			return vec[0 : i] + [vec[i] + step] + vec[i + 1 :]
		return vec

	# Crossover
	def crossover(r1, r2):
		i = random.randint(1, len(domain) - 2)

		return r1[0 : i] + r2[i :]

	# Initial population
	pop = []
	for i in range(popSize):
		vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
		pop.append(vec)

	topElite = int(elite * popSize)

	preTopScore = 0
	noImprove = 0
	for i in range(maxIter):
		scores = [(costf(v), v) for v in pop]
		scores.sort()
		ranked = [v for (s, v) in scores]

		pop = ranked[0 : topElite]

		while len(pop) < popSize:
			if random.random() < mutPorb:
				c = random.randint(0, topElite)
				pop.append(mutate(ranked[c]))
			else:
				c1 = random.randint(0, topElite)
				c2 = random.randint(0, topElite)
				pop.append(crossover(ranked[c1], ranked[c2]))

		if preTopScore == scores[0][0]:
			noImprove += 1
			if (noImprove == maxNoImproveIter):
				print "no improvement in 10 iterations"
				break 
		else:
			noImprove = 0

		preTopScore = scores[0][0]

	return scores[0][1]
