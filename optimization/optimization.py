import time
import random
import math
people = [('Seymour', 'BOS'),
            ('Franny', 'DAL'),
            ('Zooey', 'CAK'),
            ('Walt', 'MIA'),
            ('Buddy', 'ORD'),
            ('Les', 'OMA')]

destination = 'LGA'

flights = {}

for line in file('../resources/schedule.txt'):
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
        
        index = d * 2
        out = flights[(origin, destination)][r[index]]
        ret = flights[(destination, origin)][r[index + 1]]
        
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin,
                                                      out[0], out[1], out[2], 
                                                      ret[0], ret[1], ret[2])

def scheduleCost( solution ):
    totalPrice = 0
    latestArrival = 0
    earliestDepature = 24*60
    
    for d in range( len(solution)/2 ):
        origin = people[d][1]
        index = d * 2
        outBound = flights[(origin, destination)][int(solution[index])]
        returnFlight = flights[(destination, origin)][int(solution[index+1])]
        
        totalPrice += outBound[2]
        totalPrice += returnFlight[2]
        
        if latestArrival < getMinutes(outBound[1]):
            latestArrival = getMinutes(outBound[1])
        if earliestDepature > getMinutes(returnFlight[0]):
            earliestDepature = getMinutes(returnFlight[0])
            
    totalWait = 0
    for d in range(len(solution)/2):
        origin = people[d][1]
        index = d * 2
        outBound = flights[ (origin, destination) ][ int(solution[index]) ]
        returnFlight = flights[ (destination, origin) ][ int(solution[index+1]) ]
        totalWait += latestArrival - getMinutes( outBound[1] )
        totalWait += getMinutes(returnFlight[0]) - earliestDepature
        
    return totalPrice + totalWait

def randomOptimize( domain, costFunction ):
    best = 999999999
    bestSolution = None
    
    for i in range(1000):
        if i % 100 == 0:
            print i
        randomSolution = [ random.randint(domain[j][0], domain[j][1]) for j in range(len(domain)) ]
        cost = costFunction( randomSolution )
        if cost < best:
            best = cost
            bestSolution = randomSolution
            
    return bestSolution

def hillClimbingOptimize(domain, costFunction):
    solution = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain)) ]
    
    while True:
        neighbors = []
        
        for j in range(len(solution)):
            if solution[j] >= domain[j][0] and solution[j] < domain[j][1]:
                    neighbors.append(solution[:j] + [ solution[j]+1 ] + solution[j+1:])
            if solution[j] <= domain[j][1] and solution[j] > domain[j][1]:
                neighbors.append(solution[:j] + [ solution[j]-1 ] + solution[j+1:])
                
        currentCost = costFunction( solution )
        bestCost = currentCost
            
        for neighbor in neighbors:
            cost = costFunction( neighbor )
            if cost < bestCost:
                bestCost = cost
                solution = neighbor                
                        
        if bestCost == currentCost:
            break
    return solution

def annealingOptimize(domain, costFunction, T=10000000.0, cool=0.99, step=1):
    solution = [int(random.randint(domain[i][0], domain[i][1])) for i in range(len(domain))]
        
    while T > 0.1:
        index = random.randint( 0, len(domain) - 1 )
        direction = random.randint( -step, step )
        
        newSolution = solution
        newSolution[index] += direction
        
        if newSolution[index] > domain[index][1]:
            newSolution[index] = domain[index][1]
        if newSolution[index] < domain[index][0]:
            newSolution[index] = domain[index][0]
            
        energeSolution = costFunction( solution )
        energeNewSolution = costFunction( newSolution )
        
        prob = pow( math.e, (-energeNewSolution-energeSolution)/T )
        if energeNewSolution < energeSolution or random.random() < prob:
            solution = newSolution        
        T *= cool
    return solution

def geneticOptimize(domain, 
                    costFunction, 
                    popSize=50, 
                    step=1, 
                    mutProb=0.2, 
                    elite = 0.2, 
                    maxIter = 200):
    def mutate(solution):
        index = random.randint(0, len(domain)-1)
        if random.random() < 0.5 and solution[index] >= domain[index][0] and solution[index] < domain[index][0]:
            return solution[:index] + [ solution[index] + 1 ] + solution[index+1:]
        else:
            return solution[:index] + [ solution[index] - 1 ] + solution[index+1:]
     
    def crossover(r1, r2):
        index = random.randint(1, len(domain)-2)
        return r1[:index] + r2[index:]
        
    solutions = [ [ random.randint(domain[i][0], domain[i][1]) for i in range(len(domain)) ] for j in range(popSize) ]
    topElite = int( elite * popSize )
    
    for i in range(maxIter):
        scores = [(costFunction(v), v) for v in solutions]
        scores.sort()
        ranked = [v for (s,v) in scores]
        solutions = ranked[:topElite]
        
        while len(solutions) < popSize:
            if random.random() < mutProb: #mutation
                c = random.randint( 0, topElite )
                solutions.append( mutate(ranked[c]) )
            else: #crossover
                c1 = random.randint(0, topElite)
                c2 = random.randint(0, topElite)
                solutions.append(crossover(ranked[c1], ranked[c2]))
        
        print scores[0][0]
    
    return scores[0]
                
        
domain = [ (0,8) ] * len(people) * 2
solution = geneticOptimize(domain, scheduleCost)
print "cost:", scheduleCost(solution[1])
printSchedule(solution[1])
