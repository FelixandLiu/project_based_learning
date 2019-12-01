import sys
import re
from nltk import PorterStemmer
from collections import defaultdict
from array import array
import gc
import math
porter = PorterStemmer()
class CreateIndex:
    def __init__(self):
        self.index = defaultdict(list)
        self.titleIndex = {}
        self.tf = defaultdict(list)
        self.df = defaultdict(int)
        self.numDocuments = 0

    def getStopwords(self):
        f = open(self.stopwordsFile, 'r')
        stopwords = [line.rstrip() for line in f]
        self.sw = dict.fromkeys(stopwords)
        f.close()

    def getTerms(self, line):
        line = line.lower()
        line = re.sub(r'[^a-z0-9]',' ',line)
        line = line.split()
        line = [x for x in line if x not in self.sw]
        line = [porter.stem(word) for word in line]
        return line

    def parseCollection(self):
        doc = []
        for line in self.collFile:
            if line == '</page>\n':
                break
            doc.append(line)
        curPage = ''.join(doc)
        pageid = re.search('<id>(.*?)</id>', curPage, re.DOTALL)
        pagetitle = re.search('<title>(.*?)</title>', curPage, re.DOTALL)
        pagetext = re.search('<text>(.*?)</text>', curPage, re.DOTALL)
        if pageid == None or pagetitle == None or pagetext == None:
            return {}
        d = {}
        d['id'] = pageid.group(1)
        d['title'] = pagetitle.group(1)
        d['text'] = pagetext.group(1)
        return d

    def writeIndexToFile(self):
        f = open(self.indexFile, 'w')
        print(self.numDocuments, file=f)
        self.numDocuments = float(self.numDocuments)
        for term in iter(self.index.keys()):
            postinglist = []
            for p in self.index[term]:
                docID = p[0]
                positions = p[1]
                postinglist.append(':'.join([str(docID), ','.join(map(str,positions))]))
            postingData = ';'.join(postinglist)
            tfData = ','.join(map(str,self.tf[term]))
            idfData = '%.4f' % (self.numDocuments / self.df[term])
            print('|'.join((term, postingData, tfData, idfData)),file=f)
        f.close()

        f=open(self.titleIndexFile, 'w')
        for pageid, title in iter(self.titleIndex.items()):
            print(pageid,title, file=f)
        f.close()

    def getParams(self):
        param = sys.argv
        self.stopwordsFile = param[1]
        self.collectionFile = param[2]
        self.indexFile = param[3]
        self.titleIndexFile=param[4]

    def createIndex(self):
        self.getParams()
        self.collFile = open(self.collectionFile, 'r')
        self.getStopwords()
        gc.disable()
        pagedict = {}
        pagedict = self.parseCollection()
        while pagedict !={}:
            lines = '\n'.join((pagedict['title'],pagedict['text']))
            pageid = int(pagedict['id'])
            terms = self.getTerms(lines)
            self.titleIndex[pagedict['id']]=pagedict['title']
            self.numDocuments+=1
            termdictPage = {}
            for position, term in enumerate(terms):
                try:
                    termdictPage[term][1].append(position)
                except:
                    termdictPage[term] = [pageid, array('I', [position])]

            norm = 0
            for term, posting in iter(termdictPage.items()):
                norm += len(posting[1])**2
            norm = math.sqrt(norm)

            for term, posting in iter(termdictPage.items()):
                self.tf[term].append('%.4f' % (len(posting[1])/norm))
                self.df[term]+=1
            for termpage, postingpage in iter(termdictPage.items()):
                self.index[termpage].append(postingpage)

            pagedict = self.parseCollection()

        gc.enable()
        self.writeIndexToFile()

if __name__ == '__main__':
    c = CreateIndex()
    c.createIndex()