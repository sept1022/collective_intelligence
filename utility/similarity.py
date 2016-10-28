from math import *

def pearson(v1, v2):
    sum1 = sum(v1)
    sum2 = sum(v2)
    
    squareSum1 = sum( [ pow(v,2) for v in v1 ] )
    squareSum2 = sum( [ pow(v,2) for v in v2 ] )
    
    dotSum = sum( [ v1[i] * v2[i] for i in xrange(len(v1))])
    
    num = dotSum - (sum1*sum2/len(v1))
    den = sqrt((squareSum1-pow(sum1, 2)/len(v1)) * (squareSum2-pow(sum2,2)/len(v1)))
    if den == 0:
        return 0
    else:
        return 1.0-num/den