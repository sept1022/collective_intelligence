from math import sqrt

# A dictionary of movie critics and their ratings of a small
# set of movies
critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5, \
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, \
 'The Night Listener': 3.0}, \
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, \
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, \
 'You, Me and Dupree': 3.5}, \
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0, \
 'Superman Returns': 3.5, 'The Night Listener': 4.0}, \
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, \
 'The Night Listener': 4.5, 'Superman Returns': 4.0, \
 'You, Me and Dupree': 2.5}, \
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, \
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0, \
 'You, Me and Dupree': 2.0}, \
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, \
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5}, \
'Toby': {'Snakes on a Plane':4.5, 'You, Me and Dupree':1.0, 'Superman Returns':4.0}}

def sim_distance( prefs, first_person, second_person ):
    si = {}

    for item in prefs[first_person]:
        
        if item in prefs[second_person]:
            si[item] = 1
            
        if len(si) == 0:
            return 0
        
        sum_of_square = sum( [pow(prefs[first_person][item] - prefs[second_person][item], 2) 
                              for item in prefs[first_person] if item in prefs[second_person] ] )
        
        return 1/(1+sqrt(sum_of_square))

def sim_pearson( prefs, first_person, second_person ):
    si = {}

    for item in prefs[first_person]:
        if item in prefs[second_person]:
            si[item] = 1
        
    n = len( si )
    if n == 0:
        return 0
    
    sum_first = sum(prefs[first_person][it] for it in si )
    sum_second = sum(prefs[second_person][it] for it in si )
    square_sum_first = sum( [ pow( prefs[first_person][it], 2) for it in si ] )
    square_sum_second = sum( [ pow( prefs[second_person][it], 2) for it in si ] )
    
    dot_sum = sum( [ prefs[first_person][it] * prefs[second_person][it] for it in si ] )
    
    num = dot_sum - ( sum_first * sum_second / n )
    #first = (square_sum_first - pow(sum_first, 2) / n )
    #second = (square_sum_second - pow(sum_second, 2) / n ) 
    
    den = sqrt( (square_sum_first - pow(sum_first, 2) / n ) * (square_sum_second - pow(sum_second, 2) / n ) )
    if den == 0:
        return 0
    
    return num/den
        
    
def topMatches( prefs, person, n=5, similarity=sim_pearson):
    scores = [ ( similarity(prefs, person, other), other) for other in prefs if other != person ]
    
    scores.sort()
    scores.reverse()
    return scores[:n]

def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    
    for other in prefs:
        if other == person:
            continue
        sim = similarity( prefs, person, other)
        
        if sim < 0:
            continue
        
        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item,0)
                totals[item] += prefs[other][item] * sim
                simSums.setdefault(item, 0)
                simSums[item] += sim
                
    rankings = [ (total/simSums[item], item) for item,total in totals.items() if simSums[item] != 0]
    
    rankings.sort(cmp=None, key=None, reverse=True)
    return rankings

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result

def calculateSimilarItems(prefs, n=10):
    result = {}
    itemPrefs = transformPrefs(prefs) 
    count = 0
    for item in itemPrefs:
        count += 1
        if count % 100 == 0:
            print "%d / %d" % (count, len(itemPrefs))
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores    
    return result
        
def getRecommentedItems(prefs, itemSimilairity, user):
    userRatings = prefs[user]
    scores = {}
    totalScore = {}
    
    for (userItem, rating) in userRatings.items():
        for (similarity, otherItem) in itemSimilairity[userItem]:
            if otherItem in userRatings:
                continue
            
            scores.setdefault(otherItem, 0)
            scores[otherItem] += similarity*rating
            
            totalScore.setdefault(otherItem, 0)
            totalScore[otherItem] += similarity
    
    rankings = [(score/totalScore[item], item) for item,score in scores.items() if totalScore[item] != 0]
    rankings.sort(cmp=None, key=None, reverse=True)
    return rankings

def loadMovielens( path='../ml-100k'):
    
    movies = {}
    for line in open(path+"/u.item"):
        (id, title) = line.split('|')[0:2]
        movies[id] = title
        
    prefs = {}
    for line in open(path+'/u.data'):
        (user, movieId, ratings, timeStamp) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieId]] = float(ratings)
    
    return prefs

prefs = loadMovielens()
#print getRecommendations(prefs, '87' )
itemSimilarity = calculateSimilarItems(prefs, n=50)
print getRecommentedItems(prefs, itemSimilarity, '87')[:30]

