import re
import math

def getWords(doc):
    splitter = re.compile("\\W*")
    words = [word.lower() for word in splitter.split(doc) if len(word) > 2 and len(word) < 20]
    return dict([ (word, 1) for word in words ])

class Classifier:
    def __init__(self, getFeatures, fileName=None):
        self.featureCategory={}
        self.categoryCount={}
        self.getFeatures = getFeatures
        
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

class NaiveBayesClassifier(Classifier):
    def documentProb(self, item, category):
        features = self.getFeatures(item)
        
        prob = 1
        
        for feature in features:
            prob *= self.weightedProb(feature, category, self.featureProb )

        return prob
    
    def prob(self, item, category ):
        categoryProb = float(self.getCategoryCount(category)) / self.getTotalCount()
        documentProb = self.documentProb(item, category)
        return categoryProb * documentProb
        
def sampleTrain(classifier):
    classifier.train( 'Nobody owns the water.', 'good' )
    classifier.train( 'the quick rabbit jomps fences', 'good' )
    classifier.train( 'buy pharmaceuticals now', 'bad' )
    classifier.train( 'make quick money at the online casino', 'bad' )
    classifier.train( 'the quick brown fox jomps', 'good' )        
        
classifier = NaiveBayesClassifier(getWords)
sampleTrain(classifier)
print classifier.prob('quick rabbit', 'good')
print classifier.prob('quick rabbit', 'bad')

