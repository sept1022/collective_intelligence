from recommendation.data import critics

from math import sqrt

def sim_distance(prefs, left, right):
    sim = {}
    for item in prefs[left]:
        for item in prefs[right]:
            sim[item] = 1


    if len(sim) == 0:
        return 0

    sum_of_squares =sum([pow(prefs[left][item] - prefs[right][item], 2)
                         for item in prefs[left] if item in prefs[right]])

    return 1 / (1 + sqrt(sum_of_squares))

print(sim_distance(critics, 'Lisa Rose', 'Gene Seymour'))

def sim_pearson(prefs, left, right):
    sim = {}

    sim = set(prefs[left].keys()) & set(prefs[right].keys())
    n = len(sim)

    if n == 0:
        return 0

    left_sum = sum([prefs[left][item] for item in sim])
    right_sum = sum([prefs[right][item] for item in sim])

    left_square_sum = sum([prefs[left][item] ** 2 for item in sim])
    right_square_sum = sum([prefs[right][item] ** 2 for item in sim])

    p_sum = sum([prefs[left][item] * prefs[right][item] for item in sim])

    numerator = p_sum - (left_sum * right_sum / n)
    denominator = sqrt((left_square_sum - left_sum ** 2 / n) * (right_square_sum - right_sum ** 2 / n))

    if denominator == 0:
        return 0

    return numerator / denominator

print('- User based - ')
print(sim_pearson(critics, 'Lisa Rose', 'Gene Seymour'))

def top_matches(prefs, pivot, n=5, sim_function=sim_pearson):
    scores = [(sim_function(prefs, pivot, other), other) for other in prefs if other != pivot]

    scores.sort()
    scores.reverse()
    return scores[:n]

print('top matches for \'%s\'' % 'Toby', top_matches(critics, 'Toby', n=3))

def get_recommendations(prefs, pivot, sim_function=sim_pearson):
    totals = {}
    sim_sums = {}

    for other in prefs:
        if other == pivot: continue

        sim = sim_function(prefs, pivot, other)

        if sim <= 0: continue

        for item in prefs[other]:
            if item not in prefs[pivot] or prefs[pivot][item] == 0:
                totals.setdefault(item, 0.0)
                totals[item] += prefs[other][item] * sim
                sim_sums.setdefault(item, 0.0)
                sim_sums[item] += sim

    rankings = [(total/sim_sums[item], item) for item, total in totals.items()]

    rankings.sort()
    rankings.reverse()
    return rankings

print('recommendation for %s' % 'Toby', get_recommendations(critics, 'Toby'))

print('- item based -')

def transform_prefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            result[item][person] = prefs[person][item]
    return result

movies = transform_prefs(critics)
print('top matche for \'Superman Returns\'', top_matches(movies, 'Superman Returns'))
print('recommendation for %s' % 'Just My Luck', get_recommendations(movies, 'Just My Luck'))


print('----------------------------')
# item-based

def calculate_similar_items(prefs, n=10):
    result = {}
    item_prefs = transform_prefs(prefs)
    c = 0

    for item in item_prefs:
        c += 1
        if c % 100 == 0: print('%d / %d' (c, len(item_prefs)))

        scores = top_matches(item_prefs, item, n=n, sim_function=sim_distance)
        result[item] = scores

    return result

item_similarity = calculate_similar_items(critics)

for k, v in item_similarity.items():
    print(k, v)

def get_recommended_item(prefs, item_matches, user):
    user_ratings = prefs[user]
    scores = {}
    total_sim = {}

    for item, ratings in user_ratings.items():
        print(user, '|', item, '|', ratings)

        for similarity, target in item_matches[item]:

            if target in user_ratings: continue

            scores.setdefault(target, 0)
            scores[target] += similarity * ratings
            print('\t', target, similarity, similarity * ratings, 'accumulated:', scores[target])

            total_sim.setdefault(target, 0)
            total_sim[target] += similarity

    rankings = [(score/total_sim[item], item) for item, score in scores.items()]

    rankings.sort()
    rankings.reverse()
    return rankings

print(get_recommended_item(critics, item_similarity, 'Toby'))