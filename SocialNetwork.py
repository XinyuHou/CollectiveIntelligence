import math
from PIL import Image, ImageDraw
people = ['Charlie', 'Augustus', 'Veruca', 'Violet', 'Mike', 'Joe', 'Willy', 'Miranda']

links = [
		('Augustus', 'Willy'),
		('Mike', 'Joe'),
		('Violet', 'Augustus'),
		('Miranda', 'Mike'),
		('Miranda', 'Willy'),
		('Charlie', 'Mike'),
		('Veruca', 'Joe'),
		('Miranda', 'Augustus'),
		('Willy', 'Augustus'),
		('Joe', 'Charlie'),
		('Veruca', 'Augustus'),
		('Miranda', 'Joe')
		]

domain = [(10, 370)] * (len(people) * 2)

def crossCount(v):
	# Convert the number list into a dictionary of person:(x,y)
	loc = dict([(people[i], (v[i * 2], v[i * 2 + 1])) for i in range(0, len(people))])

	total = 0

	for i in range(len(links)):
		for j in range(i + 1, len(links)):

			(x1, y1), (x2, y2) = loc[links[i][0]], loc[links[i][1]]
			(x3, y3), (x4, y4) = loc[links[j][0]], loc[links[j][1]]

			den = (y4 -y3) * (x2 - x1) - (x4 -x3) * (y2 - y1)

			if den == 0:
				continue

			ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / float(den)
			ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / float(den)
			if ua > 0 and ua < 1 and ub > 0 and ub < 1:
				total += 1

	for i in range(len(people)):
		for j in range(i + 1, len(people)):
			# Get the locations of the two nodes
			(x1, y1),(x2, y2)=loc[people[i]], loc[people[j]]

			# Find the distance between them
			dist = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
			# Penalize any nodes closer than 50 pixels
			if dist < 50:
				total += (1.0 - (dist / 50.0))		

	return total

def drawNetwork(sol):
	img = Image.new('RGB', (400, 400), (255, 255, 255))
	draw = ImageDraw.Draw(img)

	pos = dict([(people[i], (sol[i * 2], sol[i * 2 + 1])) for i in range(0, len(people))])

	for (a, b) in links:
		draw.line((pos[a], pos[b]), fill = (255, 0, 0))

	for n, p in pos.items():
		draw.text(p, n, (0, 0, 0))

	img.show()

def anglePenalization(v):
	score = crossCount(v)

	# Convert the number list into a dictionary of person:(x,y)
	loc = dict([(people[i], (v[i * 2], v[i * 2 + 1])) for i in range(0, len(people))])

	for i in range(len(people)):
		outLinks = []
		inLinks = []

		for j in range(len(links)):
			if links[j][0] == people[i]:
				outLinks.append(j)
			elif links[j][1] == people[i]:
				inLinks.append(j)

		totalLinks = outLinks + inLinks

		for k in range(len(totalLinks)):
			for l in range(k + 1, len(totalLinks)):
				link1 = links[totalLinks[k]]
				link2 = links[totalLinks[l]]

				(x1, y1), (x2, y2) = loc[link1[0]], loc[link1[1]]
				(x3, y3), (x4, y4) = loc[link2[0]], loc[link2[1]]

				if x1 != x3 and y1 != y3:

					origin = loc[people[i]]
					if x1 != origin[0] and y1 != origin[1]:
						x2 = x1
						y2 = y1
						x1 = origin[0]
						y1 = origin[1]

					if x3 != origin[0] and y3 != origin[1]:
						x4 = x3
						y4 = y3
						x3 = origin[0]
						y3 = origin[1]

				left = (x2 - x1) * (x4 - x3) + (y2 - y1) * (y4 - y3)
				len1 = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
				len2 = math.sqrt(math.pow(x3 - x4, 2) + math.pow(y3 - y4, 2))

				cos = left / (len1 * len2)
				cosMin = math.cos(math.radians(15))

				if (cos > cosMin and cos != 1):
					print "angle penalty: %f" % (cos * 50)
					print link1
					print link2
					score += (cos * 50)

	return score



