import urllib2
import BeautifulSoup
import re
from urlparse import urljoin
from sqlite3 import dbapi2 as sqlite

class Crawler:
    ignoreWords = set()
    
    def __init__(self, databasePath):
        self.con = sqlite.connect(databasePath)
        self.ignoreWords = set([ 'the', 'of', 'to', 'and', 'a', 'in', 'is', 'it' ])
            
    def __del__(self):
        self.con.close()
    
    def commit(self):
        self.con.commit()
        
    def createIndexTable(self):
        self.con.execute('create table url_list(url)')
        self.con.execute('create table word_list(word)')
        self.con.execute('create table word_location(url_id, word_id, location)')
        self.con.execute('create table link(from_id integer, to_id integer)')
        self.con.execute('create table link_words(word_id, link_id)')
        self.con.execute('create index word_idx on word_list(word)')
        self.con.execute('create index url_idx on url_list(url)')
        self.con.execute('create index word_url_idx on word_location(word_id)')
        self.con.execute('create index url_to_index on link(to_id)')
        self.con.execute('create index url_from_index on link(from_id)')
        self.commit()
    
    def getEntryId(self, table, field, value, create=True):
        selectQuery = "select rowid from %s where %s = '%s'" % ( table, field, value )
        current = self.con.execute( selectQuery ) 
        result = current.fetchone()
        
        if result == None:
            insertQuery = "insert into %s (%s) values( '%s' )" % (table, field, value)
            current = self.con.execute( insertQuery )
            return current.lastrowid
        else:
            return result[0]
    
    def addToIndex(self, url, soup):
        if self.isIndexed(url) == True:
            return
        
        print 'Indexing %s' % url
        
        text = self.getTextOnly(soup)
        words = self.separateWords(text)
        
        urlId = self.getEntryId('url_list', 'url', url)
        
        for i in range(len(words)):
            word = words[i]
            if word in self.ignoreWords:
                continue
            
            wordId = self.getEntryId('word_list', 'word', word )
            query = "insert into word_location(url_id, word_id, location) values ( %d, %d, %d )" % (urlId, wordId, i)
            self.con.execute(query)
        
        
    def getTextOnly(self, soup):
        origin = soup.string
        if origin == None:
            content = soup.contents
            resultText = ''
            for text in content:
                subText = self.getTextOnly(text)
                resultText += subText
            return resultText
        else:
            return origin.strip()
            
    def separateWords(self,text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s != '' ]
    
    def isIndexed(self, url):
        urlSelectQuery = "select rowid from url_list where url='%s'" % (url)
        urlResult = self.con.execute( urlSelectQuery ).fetchone()
        
        if urlResult != None:
            wordSelectQuery = "select * from word_location wehre url_id=%d" % urlResult[0]
            wordResult = self.con.execute( wordSelectQuery ).fetchone()
            if wordResult != None:
                return False
        return True
            
        
    def addLinkRef(self, urlFrom, urlTo, linkText):
        pass
    
    def crawl(self, pages, depth=2):
        for i in range(depth):
            newPages = set()
            for page in pages:
                try:
                    content = urllib2.urlopen(page)
                except:
                    print "Could not open %s" % page
                    continue
                    
                soup = Beaut
                ifulSoup( content.read() )
                self.addToIndex(page, soup)
                
                links = soup('a')
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urljoin(page, link['href'] )
                        if url.find("'") != -1: 
                            continue
                        url = url.split('#')[0]
                        if url[0:4] == 'http' and not self.isIndexed(url):
                            newPages.add(url)
                        linkText = self.getTextOnly(link)
                        self.addLinkRef( page, url, linkText )
                self.commit()
            pages = newPages    
    
crawler = Crawler('search_index.db')
#crawler.createIndexTable()
crawler.crawl(['https://kiwitobes.com/2013/08/22/a-hack-journal/'])