from nltk.util import ngrams
from string import punctuation
from collections import Counter
from nltk import word_tokenize, pos_tag, sent_tokenize

import nltk
import string
import itertools

class CharacterAnalyzer:
    """
    Extracts character based features from the supplied text
    
    Inputs:
        input_text: string containing the raw text
        pos_tagged: the data above tokenized and pos tagged
    """
    def __init__(self, input_text, pos_tagged = None, n_grams_len = [2,3,4]):
        self.text = input_text
        if pos_tagged is not None:
            self.pos_tagged = pos_tagged
        else:
            tokens = word_tokenize(input_text)
            self.pos_tagged = pos_tag(tokens)
        
        self.numchar = len(input_text)
        self.letter_counter()
        self.freq_POS()
        self.n_grams_len = n_grams_len
        
        
    def get_n_grams(self, n):
        """
    class method for extracting character ngrams from text
    
    input:
        n  - int, length of 
        
    return:
        dict, including ngrams and their counts
        """
        #text is a string, n is length of nGrams
        txt = (self
               .text
               .lower()
               .replace("\n", " ")
               .replace("\t", " ")
               .translate(string.maketrans("",""),
                          string.punctuation))
        
        generated_ngrams = ngrams(txt, n)
        ngrams_statistics = {}

        for ngram in generated_ngrams:
            t = ''.join(ngram)
            if not t in ngrams_statistics:
                ngrams_statistics[t] = 1
            else:
                ngrams_statistics[t] += 1

        return ngrams_statistics
  
    #punctuation usage
    def letter_counter(self):
        """
        Class method extracting letter count statistics
        """
        counts = Counter(self
                         .text
                         .lower()
                         .replace("\n", " ")
                         .replace("\t", " "))
        #count punctuation characters
        self.punc_count =  sum([v for k,v in counts.iteritems() if k in punctuation])
        self.letter_count = counts

        #upper / low case ratio, digits / alphabetical ratio, 
        counts_casesen = Counter(self.text)
        self.uppcase_ratio = sum([v for k,v in counts_casesen.iteritems() if k.isupper()]) / float(self.numchar)
        self.lowcase_ratio = sum([v for k,v in counts_casesen.iteritems() if k.islower()]) / float(self.numchar)
        self.digit_ratio = sum([v for k,v in counts_casesen.iteritems() if k.isdigit()]) / float(self.numchar)
        

    #get POS frequencies
    def freq_POS(self):
        """
        Class method returning counts of pos tags
        """
        pos_tags = list(itertools
                        .chain
                        .from_iterable(self.pos_tagged)) 
        pos_freq = {}
        for (word,tag) in pos_tags:
            if not tag in pos_freq:
                pos_freq[tag] = 1
            else:
                pos_freq[tag] += 1

        self.pos_freq = pos_freq
    
    #ngrams
    def get_result(self):
        """
        class method returning all characters features as dictionary
        """
        result = {}
        result["numchar"] = self.numchar
        result["punc_count"] = self.punc_count
        result.update(self.letter_count)
        result["uppcase_ratio"] = self.uppcase_ratio
        result["lowcase_ratio"] = self.lowcase_ratio
        result["digit_ratio"] = self.digit_ratio
        
        #character nGrams
        for l in self.n_grams_len:
            result.update(self.get_n_grams(l))
        
        #POS counts
        result.update(self.pos_freq)
        return result


#helper function for testing
def ie_preprocess(document):  #preprocessing done externaly 
    sentences = sent_tokenize(document) 
    sentences = [word_tokenize(sent) for sent in sentences] 
    sentences = [pos_tag(sent) for sent in sentences]
    return sentences

def test():
    # This func for test, and it also show hwo to use this calss
    text ="""On the basis of Resnik's work, Jiang Conrath (Jiang Conrath 1997) further
    assumed that a combination of information content and edge-counting will improve the 
    correlation co-efficient (compared with human judgment). They also considered the link 
    type, depth, conceptual density, and information
    content of concepts. Concepts simplified formula can be expressed as follows.
    """
    sentences = ie_preprocess(text)
    #print sentences
    chars = CharacterAnalyzer(text, sentences)
    print chars.get_result()
    
#test()





