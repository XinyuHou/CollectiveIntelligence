from math import sqrt

# A dictionary of movie critics and their ratings of a small set of movie
critics = {
    'Lisa Rose' : {
        'Lady in the Water' : 2.5,
        'Snakes on a Plane' : 3.5,
        'Just My Luck' : 3.0,
        'Superman Returns' : 3.5,
        'You, Me and Dupree' : 2.5,
        'The Night Listener' : 3.0
    },

    'Gene Seymour' : {
        'Lady in the  Water' : 3.0,
        'Snakes on a Plane' : 3.5,
        'Just My Luck' : 1.5,
        'Superman Returns' : 5.0,
        'You, Me and Dupree' : 3.5,
        'The Night Listener' : 3.0
    },

    'Michael Philips' : {
        'Lady in the  Water' : 2.5,
        'Snakes on a Plane' : 3.0,
        'Just My Luck' : 3.0,
        'Superman Returns' : 3.5,
        'The Night Listener' : 4.0
    },

    'Claudia Puig' : {
        'Snakes on a Plane' : 3.5,
        'Just My Luck' : 3.0,
        'Superman Returns' : 4.0,
        'You, Me and Dupree' : 2.5,
        'The Night Listener' : 4.5
    },

    'Mike LaSalle' : {
        'Lady in the  Water' : 3.0,
        'Snakes on a Plane' : 4.0,
        'Just My Luck' : 2.0,
        'Superman Returns' : 3.0,
        'You, Me and Dupree' : 2.0,
        'The Night Listener' : 3.0
    },

    'Jack Matthews' : {
        'Lady in the  Water' : 3.0,
        'Snakes on a Plane' : 4.0,
        'Superman Returns' : 5.0,
        'You, Me and Dupree' : 3.5,
        'The Night Listener' : 3.0
    },

    'Toby' : {
        'Snakes on a Plane' : 4.5,
        'Superman Returns' : 4.0,
        'You, Me and Dupree' : 1.0
    }
}

# Returns a distance-basd similarity score for person1 and person2
def sim_distance(prefs, person1, person2) :
    # Get the list of shared_items
    si = {}
    for item in prefs[person1] :
        if item in prefs[person2] :
            si[item] = 1

    # If they have no rating s in common return 0
    if len(si)== 0 :
        return 0

    # Add up the squares of all the differences
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) for item in si])

    return 1 / (1 + sqrt(sum_of_squares))

# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, person1, person2) :
    # Get the list of shared_items
    si = {}
    for item in prefs[person1] :
        if item in prefs[person2] :
            si[item] = 1

    n = len(si)
    # If they have no rating s in common return 0
    if n == 0 :
        return 0

    # Add up all the preferences
    sum1 = sum([prefs[person1][item] for item in si])
    sum2 = sum([prefs[person2][item] for item in si])

    # Sum up the squares
    sum1Sq = sum([pow(prefs[person1][item], 2) for item in si])
    sum2Sq = sum([pow(prefs[person2][item], 2) for item in si])

    # Sum up the products
    productSum = sum([prefs[person1][item] * prefs[person2][item] for item in si])

    # Calculate Pearson score
    num = productSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0 :
        return 0

    r = num / den

    return r

# Return the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n = 5, similarity = sim_pearson) :
    scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]

    # Sort the list so the highest scores appear at the top
    scores.sort()
    scores.reverse()

    return scores[0 : n]

# Gets recommendations for a person by using a weighted average of every other user's rankings
def getRecommendations(prefs, person, similarity = sim_pearson) :
    totals = {}
    simSums = {}
    for other in prefs:
        if other == person :
            continue

        sim = similarity(prefs, person, other)

        if sim <= 0 :
            continue

        for item in prefs[other] :
            # Only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0 :
                # similarity * score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim

                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

        # Create the normalized list
        rankings = [(total / simSums[item], item) for item, total in totals.items()]

        # Return the sorted list
        rankings.sort()
        rankings.reverse()

        return rankings

def transformPrefs(prefs) :
    result = {}
    for person in prefs :
        for item in prefs[person] :
            result.setdefault(item, {})

            result[item][person] = prefs[person][item]


    return result

def calculateSimilarItems(prefs, n = 10) :
    # Create a dictionary of items showing which other items they are most similar to.
    result = {}

    # Invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)

    c = 0

    for item in itemPrefs :
        c += 1
        if c % 10 == 0 :
            print "%d / %d" % (c, len(itemPrefs))

        #Find the most similar items to this one
        scores = topMatches(itemPrefs, item, n = n, similarity = sim_distance)
        result[item] = scores

    return result
    

