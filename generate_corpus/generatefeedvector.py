# -*- coding:utf8 -*-

from generate_corpus.generatefeedparser import getwordcount

apcount = {}
wordcounts = {}

feedlist = []

for feedurl in file('../feedlist.txt'):
    
    title, wc = getwordcount(feedurl)
    
    if title == None or wc == None:
        print "ignore:", feedurl
        continue
    
    feedlist.append(feedurl)
    wordcounts[title] = wc
    for word,count in wc.items():
        apcount.setdefault(word, 0)
        if count > 1:
            apcount[word]+=1

            
wordlist = []
for w,bc in apcount.items():
    frac = float(bc)/len(feedlist)
    if frac > 0.1 and frac < 0.5:
        wordlist.append(w)
       
out = file("../blogdata.txt", "w")
out.write('Blog')

for word in wordlist:
    out.write('\t%s' % word )

out.write('\n')
for blog, wc in wordcounts.items():
    out.write(blog)
    for word in wordlist:
        if word in wc:
            out.write('\t%d' % wc[word])
        else:
            out.write('\t0')
    out.write('\n')

    