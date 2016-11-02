import re
import math
from xlwings.constants import CategoryType

def getWords(doc):
    splitter = re.compile("\\W*")
    words = [word.lower() for word in splitter.split(doc) if len(word) > 2 and len(word) < 20]
    return dict([ (word, 1) for word in words ])

class Classifier:
    def __init__(self, getFeatures=None):
        self.featureCategory={}
        self.categoryCount={}
        self.getFeatures = getFeatures
        self.thresholds = {}
        
    def increaseFeatureCount(self, feature, category):
        self.featureCategory.setdefault(feature, {})
        self.featureCategory[feature].setdefault(category, 0)
        self.featureCategory[feature][category] += 1
        
    def increaseCategoryCount(self, category):
        self.categoryCount.setdefault(category, 0)
        self.categoryCount[category] += 1
        
    def getFeatureCount(self, feature, category):
        if feature in self.featureCategory and category in self.featureCategory[feature]:
            return float( self.featureCategory[feature][category] )
        else:
            return 0.0
        
    def getCategoryCount(self, category):
        if category in self.categoryCount:
            return self.categoryCount[category]
        else:
            return 0.0
    
    def getTotalCount(self):
        return sum( self.categoryCount.values() )
    
    def getCategories(self):
        return self.categoryCount.keys()
    
    def train(self, item, category):
        features = self.getFeatures(item)
        for feature in features:
            self.increaseFeatureCount(feature, category)
            
        self.increaseCategoryCount(category)
        
    def featureProb(self, feature, category):
        if self.getCategoryCount(category) == 0:
            return 0
        else:
            return self.getFeatureCount(feature, category) / self.getCategoryCount(category)
    
    def weightedProb(self, feature, category, probFuction, weight = 1.0, assumedProb = 0.5):
        basicProb = probFuction( feature, category )
        totals = sum([self.getFeatureCount(feature, category) for category in self.getCategories() ])
        weightedAverage = ( ( weight * assumedProb ) + (totals * basicProb ) ) / ( weight + totals )
        return weightedAverage
    
    def setThreshold(self, category, threathold):
        self.thresholds[category] = threathold
        
    def getThreshold(self, category):
        if category not in self.thresholds:
            return 1.0        
        return self.thresholds[category]

class NaiveBayesClassifier(Classifier):
    def documentProb(self, item, category):
        features = self.getFeatures(item)
        
        prob = 1
        
        for feature in features:
            prob *= self.weightedProb(feature, category, self.featureProb )

        return prob
    
    def prob(self, item, category ):
        # Pr(Category|Document) = Pr(Document|Category) * Pr(Category) / Pr(Document)
        
        # Pr(Category) = count( specified category ) / count( total category )  
        # Pr(Document|Category) = Pr(Feature1) * Pr(Feature2) ...
            # Pr(Feature) = count( feature in category ) / category count
        # Pr(Document) is ignored
        
        categoryProb = float(self.getCategoryCount(category)) / self.getTotalCount()
        documentProb = self.documentProb(item, category)
        return categoryProb * documentProb
    
    def classify(self, item, default=None):
        probs = {}
        maxProb = 0.0
        bestCategory = None
        for category in self.getCategories():
            probs[category] = self.prob(item, category)
            if probs[category] > maxProb:
                maxProb = probs[category]
                bestCategory = category
                
        for (category, prob) in probs.items():
            if category == bestCategory:
                continue
            if prob * self.getThreshold(bestCategory) > maxProb:
                return default
        return bestCategory
                        
class FisherClassifier(Classifier):
    def __init__(self, getFeatures):
        Classifier.__init__(self, getFeatures)
        self.minimums = {}
        
    def setMinimum(self, category, minimum):
        self.minimums[category] = minimum
    
    def getMinimum(self, category):
        if category not in self.minimums:
            return 0
        else:
            return self.minimums[category]
        
    def categoryProb(self, feature, category):
        clf = self.featureProb(feature, category)
        if clf == 0:
            return 0
        
        frequency = sum( [self.featureProb(feature, category) for category in self.getCategories()] )
        return clf/frequency
    
    def prob(self, item, category):
        p = 1.0
        features = self.getFeatures(item)
        for feature in features:
            p *= self.weightedProb(feature, category, self.categoryProb)
            
        fscore = -2*math.log(p)
        return self.inverseChiSquare(fscore, len(features) * 2)
    
    def inverseChiSquare(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df/2):
            term *= m/i
            sum += term
        return min(sum, 1.0)
    
    def classify(self, item, default=None):
        bestCategory = default
        maxProb = 0.0
        
        for category in self.getCategories():
            prob = self.prob(item, category)
            if prob > self.getMinimum(category) and prob > maxProb:
                maxProb = prob
                bestCategory = category
        
        return bestCategory
            
                
        

def sampleTrain(classifier):
    classifier.train( 'Nobody owns the water.', 'good' )
    classifier.train( 'the quick rabbit jomps fences', 'good' )
    classifier.train( 'buy pharmaceuticals now', 'bad' )
    classifier.train( 'make quick money at the online casino', 'bad' )
    classifier.train( 'the quick brown fox jomps', 'good' )        
        
#classifier = NaiveBayesClassifier(getWords)
#sampleTrain(classifier)
#print classifier.classify('quick rabbit', default='unknown')
# #print classifier.classify('quick money', default='unknown')
# classifier.setThreshold('bad', 3.0)
# print classifier.classify('quick money', default='unknown')

classifier = FisherClassifier(getWords)
sampleTrain(classifier)
# print classifier.categoryProb('quick', 'good')
# print classifier.categoryProb('money', 'bad')
# print classifier.weightedProb('money', 'bad', classifier.categoryProb )
# print classifier.weightedProb('money', 'good', classifier.categoryProb )

print classifier.classify('quick rabbit')
print classifier.classify('quick money')
classifier.setMinimum('bad', 0.8)
print classifier.classify('quick money')





