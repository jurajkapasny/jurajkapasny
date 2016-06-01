import wordnet_analyzer
import lexical_analyzer
import character_analyzer
import string

from nltk import word_tokenize, pos_tag, sent_tokenize

import logging 
#set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#or just in console
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# ch.setFormatter(formatter)
# logger.addHandler(ch)

class NlpFeatureExtractor:
    """
    Class to extract various text based features from the raw input text 
    of arbitrary length
    """
    def __init__(self, text):
        text = filter(lambda x: x in string.printable, text)
        self.text = text
        #preprocessing the data
        try:
            sentences = sent_tokenize(text) 
            sentences = [word_tokenize(sent) for sent in sentences] 
            self.pos_tagged = [pos_tag(sent) for sent in sentences]
        except Exception as e:
            logger.error("Data preparation failed: %s" %e)
        
    def get_result(self):
        """
        Class method to run all partial extractors and return the results
        
        Returns:
            dict
        """
        results = {}
        #wordnet features
        try:
            wordnet = wordnet_analyzer.WordNetAnalyzer(self.pos_tagged, True)
            results.update(wordnet.get_result())
        except Exception as e:
            logger.error("Wordnet failed: %s" %e)
        #character features
        try:
            chars = character_analyzer.CharacterAnalyzer(self.text, self.pos_tagged)
            results.update(chars.get_result())
        except Exception as e:
            logger.error("Charfeat failed: %s" %e)
        #lexical features
        try:
            lexical = lexical_analyzer.LexicalAnalyzer(self.text)
            results.update(lexical.get_result())
        except Exception as e:
            logger.error("Lexical failed: %s" %e)
        
        return results

def test():
# This func for test, and it also show hwo to use this calss
    text ="""On the basis of Resnik's work, Jiang Conrath (Jiang Conrath 1997) further
    assumed that a combination of information content and edge-counting will improve the 
    correlation co-efficient (compared with human judgment). They also considered the link 
    type, depth, conceptual density, and information
    content of concepts. Concepts simplified formula can be expressed as follows.
    """
    nlpfeat = NlpFeatureExtractor(text)
    print nlpfeat.get_result()

#test()
