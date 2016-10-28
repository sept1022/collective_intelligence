from utility import similarity

class bicluster:
    
    def __init__(self, vec=None, left=None, right=None, distance=0.0, cluster_id=None):
        self.left_ = left
        self.right_ = right
        self.vec_ = vec
        self.id_ = cluster_id
        self.distance_ = distance
    
    def getFeature(self):
        return self.ve
        
def hcluster(rows, distance=similarity.pearson):
    distances={}
    currentClusterId = -1
    featureSize = len(rows[0])
    

    cluster = [ bicluster(rows[i], cluster_id=i) for i in range(len(rows))]
    
    
    #calculate pair weight
    while len(cluster) > 1:
        lowestPair = ( 0, 1 )
        lowestDistance = distance(cluster[0].vec_, cluster[1].vec_) 
                
        for i in range( len(cluster) ):
            for j in range( i+1, len(cluster) ):
                if ( cluster[i].id_, cluster[j].id_ ) not in distances:
                    pairDistance = distance( cluster[i].vec_, cluster[j].vec_ );
                    distances[ ( cluster[i].id_, cluster[j].id_ ) ] = pairDistance
                    if pairDistance < lowestDistance:
                        lowestDistance = pairDistance
                        lowestPair = (i,j)                
                else:
                    continue
        
        #merge two cluster
        #centroid
        newCentroid = [ ( cluster[lowestPair[0]].vec_[i] + cluster[lowestPair[1]].vec_[i] ) / 2.0 for i in range(featureSize)]
        newCluster = bicluster( vec = newCentroid, 
                                left = cluster[lowestPair[0]], 
                                right = cluster[lowestPair[1]], 
                                distance = lowestDistance, 
                                cluster_id = currentClusterId)
        
        currentClusterId -= 1
        
        cluster.append(newCluster)
        del cluster[ lowestPair[0] ]
        del cluster[ lowestPair[1] ]
    
    return cluster[0]
        
def readFile(fileName):
    lines = [line for line in file(fileName)]
    
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    
    for line in lines[1:]:
        p = line.split('\t')
        rownames.append(p[0])
        data.append([float(x) for x in p[1:]])
    return rownames, colnames, data

def printCluster(cluster, labels=None, n=0):
    for i in range(n):
        print ' ',
        
    if cluster.id_ < 0:
        print '-'
    else:
        if labels == None:
            print cluster.id_
        else:
            print labels[cluster.id_]
    if cluster.left_ != None:
        printCluster( cluster.left_, labels=labels, n=n+1 )
    if cluster.right_ != None:
        printCluster( cluster.right_, labels=labels, n=n+1 )

blognames, words, data = readFile("../blogdata.txt")
#cluster = hcluster(data)
#printCluster(cluster, blognames)

def kmeans(rows, distance=similarity.pearson,k=4):
    featureSize = len(rows[0])
    if featureSize == 0:
        print "feature size: 0"
        return
    test = (1,2)
    range = [ ( min( row[i] for row in rows ), max( [ row[i] for row in rows ] ) ) for i in range(featureSize) ]

kmeans(data, k = 5)