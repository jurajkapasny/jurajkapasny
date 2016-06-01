import nltk
from nltk.collocations import *
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
import os

try:
    __location__ = os.path.realpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__)))
    
except:
    __location__ = os.path.realpath(os.path.join(os.getcwd()))

class LexicalAnalyzer:
    """
    Class to retrieve lexical features from supplied text
    
    input:
        input_txt - string, containing the raw text
    """
    def __init__(self, input_txt):
        text = input_txt
        self.load_functional_words()
        self.sent = {}
        self.acronyms_count = 0
        self.wrd_length = {}
        self.wrd_freq = nltk.FreqDist() # for words' frequency
        self.words_count = 0
        self.word_counts = {}
        self.sentence_count = 0
        self.function_words_count = 0
        self.basic_measures(text)
        self.paragraph_count = text.count('\n\n')
        self.tokens = [word.lower() for word in wordpunct_tokenize(text)]
    
    def basic_measures(self, text):
        """
        Class method to get basic lexical features
        """
        sentences = sent_tokenize(text)
        #print sentences
        self.sentence_count = len(sentences)
        for sentence in sentences:
            words = word_tokenize(sentence)
            #print words
            try:
                #print len(sentence)
                self.sent[len(words)] += 1
            except KeyError:
                self.sent[len(words)] = 1

            for word in words:
                if word in self.word_counts:
                    self.word_counts[word] += 1
                else:
                    self.word_counts[word] = 1
                    
                if word.isupper() and len(word) > 1 and len(word) < 10:
                     self.acronyms_count += 1
                self.words_count += 1
                self.wrd_freq[word.lower()] += 1
                try:
                    self.wrd_length[len(word)] += 1 
                except KeyError:
                    self.wrd_length[len(word)] = 1
                try:
                    self.function_words[word.lower()] += 1
                    self.function_words_count += 1
                except KeyError:
                    pass

    def get_avg_sentence_length(self):
        """
        Class method to compute average sentence length
        """
        length =0
        count =0
        length2=0
        for key,value in self.sent.iteritems():
            #print key, value
            length += value * key
            length2 += value * pow(key, 2) # For getting the variance
            count += value
        
        mean = float(length) / float(count)
        variance = (float(length2) / count) - pow(mean, 2)
        return {"SNTLNGM": mean, "SNTLNGVAR": variance}
    
    def get_word_length(self):
        """
        Getter for wrd_length
        """
        return self.wrd_length
    
    def get_avg_word_length(self):
        """
        Class method to compute average word length
        """
        length=0
        count =0
        length2=0
        for key,value in self.wrd_length.iteritems():
            #print key,value
            length += value * key
            length2 += value * pow(key,2) # For getting the variance
            count += value
        
        mean = float(length) / float(count)
        variance = (float(length2) / count) - pow(mean, 2)
        return {"WRDCNTM": mean, "WRDCNTVAR": variance}
    
    def get_vocabulary_richness(self):
        """
        Class method to compute vocabulary richness
        """
        return {"VOCRCH": float(self.wrd_freq.B()) / float(self.words_count)}
        # or wrd_freq.N() 
    
    def get_hapax_legomena(self):
        """
        Class method to compute hapax legomena
        """
        #print self.wrd_freq.hapaxes()
        return {"HPXCNT" : len(self.wrd_freq.hapaxes())}
    
    def get_function_words_count(self):
        """
        Getter for words count
        """
        return {"FNCWRDCNT" : self.function_words_count}
    
    def load_functional_words(self):
        """
        Class method to load functional words from a file
        """
        self.function_words ={}
        for line in open(os.path.join(__location__, 'functionwords.txt')):
            self.function_words[line.strip().lower()] = 1
    
    def get_frequent_words(self, n):
        """
        Class method to return n frequent words
        """
        return self.wrd_freq.keys()[:n]
    
    def get_frequent_ngrams(self,words):
        """
        Class method to return frequent ngrams
        """
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        trigram_measures = nltk.collocations.TrigramAssocMeasures()
        finder = BigramCollocationFinder.from_words(words)
        finder.apply_freq_filter(3) ##ignore those occurring less than 3 times
        self.top_bigrams = finder.nbest(bigram_measures.pmi, 10) 
        finder = TrigramCollocationFinder.from_words(words)
        finder.apply_freq_filter(3) ##ignore those occurring less than 3 times
        self.top_trigrams = finder.nbest(trigram_measures.raw_freq, 10) 
    
    def get_acronyms(self):
        """
        Getter for acronyms count
        """
        return {"ACRNMCNT": self.acronyms_count}
    
    def get_paragraphs_count(self):
        """
        Getter for paragraphs count
        """
        return {"PRGCNT": self.paragraph_count}
    
    def get_sentences_count(self):
        """
        Getter for sentence count
        """
        return {"SNTCNT": self.sentence_count}
    
    def get_top_bigrams(self, n):
        """
        Class method to calculate top n bigrams
        
        input:
            n - int, number of ngrams
        """
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        finder = BigramCollocationFinder.from_words(self.tokens)
        finder.apply_freq_filter(3) #ignore those occurring less than 3 times
        top_bigrams = finder.nbest(bigram_measures.pmi, n) 
        return top_bigrams
    
    def get_top_trigrams(self, n):
        """
        Class method to calculate top n trigrams
        
        input:
            n - int, number of ngrams
        """
        trigram_measures = nltk.collocations.TrigramAssocMeasures()
        finder = TrigramCollocationFinder.from_words(self.tokens)
        finder.apply_freq_filter(3) #ignore those occurring less than 3 times
        top_trigrams = finder.nbest(trigram_measures.raw_freq, n) 
        return top_trigrams


    def get_ngram_sim(self,topn):
        """
        Class method to calculate similarity with popular ngrams
        
        input:
            topn - int, number of ngrams
        """
        gram2_wrd = self.get_top_bigrams(topn)
        gram1_wrd = self.get_frequent_words(topn)
        #print gram1_wrd
        with open(os.path.join(__location__, "count_2w.txt"),'r') as file_2gram:
            gram2 = file_2gram.readlines()
        with open(os.path.join(__location__, "count_1w.txt"),'r') as file_1gram:
            gram1 = file_1gram.readlines()
        count1 = count2 = 0
        
        for line in gram2:
            words = line.split()
            wrd1 = words[0].strip().lower()
            wrd2 = words[1].strip().lower()
            #print wrd1,wrd2
            if((wrd1,wrd2) in gram2_wrd):
                count2 +=1
        
        for line in gram1:
            (key, val) = line.strip().split()
            #print key
            
            if(key.strip() in gram1_wrd):
                count1 +=1
                
        return {"2GRMWRDSIM": float(count2) / topn, "1GRMWRDSIM": float(count1) / topn}
    
    def get_result(self):
        """
        Class method to get all features back
        """
        result = {}
        ## This will return the mean and Variance too, ignore the name :)
        result.update(self.get_avg_sentence_length()) 
        ## Same for the words, mean & Variance
        result.update(self.get_avg_word_length())
        result.update(self.get_vocabulary_richness())
        result.update( self.get_hapax_legomena() )# words that occurs only once
        result.update(self.get_function_words_count())
        #result.update(self.get_frequent_words(5))
        result.update(self.get_sentences_count())
        result.update(self.get_paragraphs_count())
        result.update(self.get_acronyms())
        result.update(self.get_ngram_sim(3000000))
        result.update(self.word_counts)
        return result

def test():

    text = "Costs for. Costs for. Costs for. Costs for." 

    #print text[:1000]
    lex = LexicalAnalyzer(text)
    #print lex.get_results()
    #print "average sentence length : ", lex.get_avg_sentence_length()
    #print "average word length:", lex.get_avg_word_length()
    #print "Richness:", lex.get_vocabulary_richness()
    #print "Hapaxes count:", lex.get_hapax_legomena() # words that occurs only once
    #print "Functional words count:", lex.get_function_words_count()
    #print "Top 5 words:" , lex.get_frequent_words(5)
    #print "Number of sentences:" , lex.get_sentences_count()
    #print "Number of paragraphs:" ,lex.get_paragraphs_count()
    #print "Top 10 Bigrams", lex.get_top_bigrams(10)
    #print "Top 10 trigrams", lex.get_top_trigrams(10)
    #print "Count acronym", lex.get_acronyms()
    return lex.get_result()

#test()

