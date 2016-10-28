from utility import similarity

class bicluster:
    left_ = None
    right_ = None
    vec_ = []
    id_ = 0
    distance_ = 0.0
    
    @classmethod
    def __init__(self, vec=None, left=None, right=None, distance=0.0, cluster_id=None):
        self.left_ = left
        self.right_ = right
        self.vec_ = vec
        self.id_ = cluster_id
        self.distance_ = distance
        
def hcluster(rows, distance=similarity.pearson):
    distances={}
    currentClusterId = -1
    
    cluster = [ bicluster(rows[i], cluster_id=i) for i in xrange(len(rows))]
    print cluster[0].vec_
    
    while len(cluster) > 1:
        lowestPair = ( 0, 1 )
        print type( cluster[0].vec_ )
        print type( cluster[1].vec_ )
        closest = distance( cluster[0].vec_, cluster[1].vec_ )
        print closest
        return
            
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

rownames, colnames, data = readFile("../blogdata.txt")
hcluster(data)

