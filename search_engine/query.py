import sys
import re
from nltk import PorterStemmer
import copy
from functools import reduce

porter = PorterStemmer()

class QueryIndex:
    def __init__(self):
        self.index = {}
        self.titleIndex ={}
        self.tf = {}
        self.idf = {}

    def intersectLists(self, lists):
        if len(lists) == 0:
            return []
        lists.sort(key=len)
        return list(reduce(lambda x,y: set(x)&set(y),lists))

    def getStopwords(self):
        f = open(self.stopwordsFile,'r')
        stopwords = [line.rstrip() for line in f]
        self.sw = dict.fromkeys(stopwords)
        f.close()

    def getTerms(self, line):
        line = line.lower()
        line = re.sub(r'[^a-z0-9]', ' ', line)
        line = line.split()
        line = [x for x in line if x not in self.sw]
        line = [porter.stem(word) for word in line]
        return line

    def getPostings(self, terms):
        return [ self.index[term] for term in terms]

    def getDocsFromPostings(self, postings):
        return [ [ x[0] for x in p] for p in postings]

    def readIndex(self):
        f = open(self.indexFile, 'r')
        self.numDocuments = int(f.readline().rstrip())
        for line in f:
            line = line.strip()
            term, postings, tf, idf, = line.split('|')
            postings = postings.split(';')
            postings = [x.split(':') for x in postings]
            postings = [ [int(x[0]), map(int, x[1].split(','))] for x in postings]
            self.index[term] = postings
            tf = tf.split(',')
            self.tf[term]=map(float,tf)
            self.idf[term] = float(idf)
        f.close()

        f=open(self.titleIndexFile,'r')
        for line in f:
            pageid, title = line.rstrip().split(' ',1)
            self.titleIndex[int(pageid)] = title
        f.close()

    def dotProduct(self, vec1, vec2):
        if len(vec1)!=len(vec2):
            return 0
        return sum( [x*y for x, y in zip(vec1, vec2)])

    def rankDocuments(self, terms, docs):
        docVectors = defaultdict(lambda: [0] *len(terms))
        queryVector = [0] *len(terms)
        for termIndex, term in enumerate(terms):
            if term not in self.index:
                continue
            queryVector[termIndex] = self.idf[term]

            for docIndex, (doc, postings) in enumerate(self.index[term]):
                if doc in docs:
                    docVectors[doc][termIndex] =self.tf[term][docIndex]

        docScores = [ [ self.dotProduct(curDocVec, queryVector), doc] for doc, curDocVec in iter(docVectors.items())]
        docScores.sort(reverse= True)
        resultDocs = [ x[1] for x in docScores][:10]
        resultDocs = [ self.titleIndex[x] for x in resultDocs]
        print('\n'.join(resultDocs), '\n')

    def queryType(self,q):
        if '"' in q:
            return 'PQ'
        elif len(q.split()) >1:
            return 'FTQ'
        else:
            return 'OWQ'

    def owq(self,q):
        originalQuery = q
        q = self.getTerms(q)
        if len(q) == 0:
            print('')
            return
        elif len(q)>1:
            self.ftq(originalQuery)
            return
        term=q[0]
        if term not in self.index:
            print('')
            return
        else:
            postings= self.index[term]
            docs = [x[0] for x in postings]
            self.rankDocuments(q, docs)

    def ftq(self,q):
        q = self.getTerms(q)
        if len(q) == 0:
            print('')
            return
        li = set()
        for term in q:
            try:
                postings = self.index[term]
                docs=[x[0] for x in postings]
                li=li|set(docs)
            except:
                pass
        li=list(li)
        self.rankDocuments(q, li)

    def pq(self,q):
        originalQuery = q
        q = self.getTerms(q)
        if len(q) == 0:
            print('')
            return
        elif len(q) == 1:
            self.owq(originalQuery)
            return
        phraseDocs = self.pqDocs(q)
        self.rankDocuments(q, phraseDocs)

    def pqDocs(self, q):
        phraseDocs = []
        length =len(q)
        for term in q:
            if term not in self.index:
                return []
        postings = self.getPostings(q)
        docs = self.getDocesFromPostings(postings)
        docs = self.intersectLists(docs)
        for i in xrange(len(postings)):
            postings[i] = [x for x in postings[i] if x[0] in docs]
        postings = copy.deepcopy(postings)

        for i in xrange(len(postings)):
            for j in xrange(len(postings[i])):
                postings[i][j][1] = [x-i for x in postings[i][j][1]]
        result = []
        for i in xrange(len(postings[0])):
            li = self.intersectLists( [x[i][1] for x in postings])
            if li ==[]:
                continue
            else:
                result.append(postings[0][i][0])
        return result

    def getParams(self):
        param = sys.argv
        self.stopwordsFile = param[1]
        self.indexFile = param[2]
        self.titleIndexFile = param[3]

    def queryIndex(self):
        self.getParams()
        self.readIndex()
        self.getStopwords()
        while True:
            q = sys.stdin.readline()
            if q == '':
                break
            qt = self.queryType(q)
            if qt =='OWQ':
                self.owq(q)
            elif qt == 'FTQ':
                self.ftq(q)
            elif qt=='PQ':
                self.pq(q)

if __name__=='__main__':
    q=QueryIndex()
    q.queryIndex()