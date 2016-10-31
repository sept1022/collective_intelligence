from sqlite3 import dbapi2 as sqlite

class Searcher:
    def __init__(self, fileName):
        self.con = sqlite.connect(fileName)
        
    def __del__(self):
        self.con.close()
        
    def getMatchRows(self, q):
        selectField = 'w0.urlid'
        tableList = ''
        clauseList = ''
        wordIds = []
        words = q.split(' ')
        tableNumber = 0
        
        
        for word in words:
            wordQuery = "select rowid from wordlist where word='%s'" % word
            wordRow = self.con.execute(wordQuery).fetchone()
            
            if wordRow != None:
                wordId = wordRow[0]
                wordIds.append(wordId)
                
                if tableNumber > 0:
                    tableList += ','
                    clauseList += ' and '
                    clauseList += 'w%d.urlid = w%d.urlid and ' % (tableNumber - 1, tableNumber)
                    
                selectField += ",w%d.location" % tableNumber
                tableList += 'wordlocation w%d' % tableNumber
                clauseList += 'w%d.wordid=%d' % (tableNumber, wordId)
                tableNumber += 1

        
        query = 'select %s from %s where %s' % (selectField, tableList, clauseList)
        queryResult = self.con.execute(query)
        rows = [row for row in queryResult]
        
        return rows, wordIds
    
    def getScoredList(self, rows, wordIds):
        totalScores = dict([(row[0], 0) for row in rows ])
        
        # for frequency score
        weights = [ (1.0, self.frequencyScore(rows) ),
                    (1.0, self.locationScore(rows) ),
                    (1.0, self.pagerankScore(rows) ) ]
        
        for weight, score in weights:
            for url in totalScores:
                totalScores[url] += weight * score[url]
                
        return totalScores
    
    def getUrlName(self, urlId):
        query = "select url from urllist where rowid=%d" % urlId
        result = self.con.execute(query).fetchone()
        return result[0]
    
    def normalizeScores(self, scores, forSmall=False):
        verySmallValue = 0.00001
        if forSmall == True:
            minScore = min(scores.values())
            return dict([ (url, float(minScore) / max(verySmallValue, score)) for(url, score) in scores.items()])
        else:
            maxScore = max(scores.values())
            if maxScore == 0:
                maxScore = verySmallValue
            return dict([ (url, float(score) / maxScore) for (url, score) in scores.items()])
        
    def frequencyScore(self, rows):
        counts = dict([(row[0], 0) for row in rows])
        for row in rows: counts[row[0]] += 1
        return self.normalizeScores(counts)

    def locationScore(self, rows):
        maxLocation = 1000000
        locations = dict([ (row[0], maxLocation) for row in rows ])
        for row in rows:
            location = sum(row[1:])
            if location < maxLocation:
                locations[row[0]] = location
        return self.normalizeScores(locations, forSmall=True)
    
    def distanceScore(self, rows):
        if len(rows[0]) <= 2:
            return dict([(row[0], 1.0) for row in rows ])
        
        minDistance = dict([(row[0], 10000000) for row in row ])
        
        for row in rows:
            distance = sum(abs(row[i] - row[i - 1]) for i in range(2, len(row)))
            if distance < minDistance[row[0]]:
                minDistance[row[0]] = distance
       
    # simple count         
    def inbounLinkScore(self, rows):
        uniqueUrls = set([row[0] for row in rows])
        inboundCount = dict()
        for url in uniqueUrls: 
            query = "select count(*) from link where toid=%d" % url
            result = self.con.execute(query).fetchone()
            print query
            inboundCount[url] = result[0]
        return self.normalizeScores(inboundCount)
    
    def pagerankScore(self, rows):
        pagerank = dict()
        
        for row in rows:
            query = "select score from pagerank where urlid=%d" % row[0]
            result = self.con.execute(query).fetchone()
            pagerank[row[0]] = result[0]
        
        maxRank = max(pagerank.values())
        normalizedScores = dict([( url, float(score)/maxRank ) for url, score in pagerank.items() ])
        return normalizedScores
            
    def calculatePageRange(self, iterations=20):
        self.con.execute('drop table if exists pagerank')
        self.con.execute('create table pagerank(urlid primary key, score)')
        self.con.execute('insert into pagerank select rowid, 1.0 from urllist')
        self.con.commit()
        
        for i in range(iterations):
            print "Iteration: %d" % i
            
            urlQuery = "select rowid from urllist"
            urlResult = self.con.execute(urlQuery)
            for (urlId,) in urlResult:
                pr = 0.15
                fromIdQuery = "select distinct fromid from link where toid=%d" % urlId
                fromIdResult = self.con.execute(fromIdQuery)
                for (linker,) in fromIdResult:
                    linkingQuery = "select score from pagerank where urlid=%d" % linker
                    linkingResult = self.con.execute(linkingQuery).fetchone()
                    linkingPr = linkingResult[0]
                    linkingCountQuery = "select count(*) from link where fromid=%d" % linker
                    linkingCountResult = self.con.execute(linkingCountQuery).fetchone()
                    linkingCount = linkingCountResult[0]
                    pr += linkingPr / linkingCount
                updateQuery = "update pagerank set score=%f where urlid=%d" % (pr, urlId)
                self.con.execute(updateQuery)
            self.con.commit();              
             
    def searchQuery(self, query):
        rows, wordIds = self.getMatchRows(query)
        scores = self.getScoredList(rows, wordIds)
        rankedScores = sorted([(score, url) for (url, score) in scores.items()], reverse=True)
        for (score, url) in rankedScores[:10]:
            print '%f\t%s' % (score, self.getUrlName(url))
        
                
e = Searcher('searchindex.db')
e.searchQuery("Functional programming")
