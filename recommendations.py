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

    