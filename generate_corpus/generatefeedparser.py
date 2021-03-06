# -*- coding:utf-8 -*-

import feedparser
import re

def getwordcount(url):
    d = feedparser.parse(url)
    wc = {}
    
    for e in d.entries:
        if 'summary' in e:
            summary = e.summary
        else:
            summary = e.description
        
        words = getwords( e.title + ' ' + summary )
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1
    
    if "title" not in d.feed or d.feed.title == "":
        return None, None
    return d.feed.title, wc
        
def getwords(html):
    txt = re.compile(r'<[^>]+>').sub('', html)
    
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    
    return [word.lower() for word in words if len(word) > 0]