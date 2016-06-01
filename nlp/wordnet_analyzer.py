from nltk.corpus import wordnet as wn
from nltk import word_tokenize, pos_tag, corpus, download, RegexpParser, sent_tokenize
from nltk.collocations import *
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus.reader.wordnet import WordNetError
import string

#take care of undecodable characters
import sys  
reload(sys)
sys.setdefaultencoding('utf8')

import logging 
#set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

PUNCT = string.punctuation
NOUN_POS = ['NNP', 'NNPS','NNS','NN']
VERB_POS = ['VB', 'VBD','VBG','VBN', 'VBP', 'VBZ']

class WordNetAnalyzer:
    """
    # This class wrap the nltk.wordnet 
    # It is initialized using a PoS tagged corpus
    # It will fisrt chunk the corpus and extract all the noun phrases (we consider only sequences of proper nouns)
    # Then for all these chunks, it will get the synset (synonyms set) from wordnet, and the min_depth of it
    """
    def __init__(self, pos_tagged_corpus, is_sentences):
        # NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and nouns
        # chunk sequences of proper nouns
        self.grammar = r"""
            NP:  {<NNP>+}                
        """
        self.entities ={}
        self.chunker = RegexpParser(self.grammar)
        self.hypernym_depth =0
        self.hypernym_v_depth =0
        self.hypernym_n_depth =0
        self.n_count=0
        self.v_count=0
        if is_sentences:
            for sentence in pos_tagged_corpus:
                self.process_data(sentence)
                self.process_hypernym(sentence)
        else:
            self.process_data(pos_tagged_corpus)
            self.process_hypernym(pos_tagged_corpus)
        self.mean_tree_depth = self.get_avg_depth()
        try:
            self.mean_hypernym_v =  float(self.hypernym_v_depth) / float(self.v_count)
        except:
            self.mean_hypernym_v = 0
        try:
            self.mean_hypernym_n =  float(self.hypernym_n_depth) / float(self.n_count)
        except:
            self.mean_hypernym_n = 0
        try:
            self.mean_hypernym =  float(self.hypernym_depth) / float(self.v_count + self.n_count)
        except:
            self.mean_hypernym = 0
    
    def get_result(self):
        """
        Class method to return all the results
        """
        result = {}
        result["ENTDepth"] = self.mean_tree_depth
        result["HYNOUNaw"] = self.mean_hypernym_n
        result["HYVERBaw"]= self.mean_hypernym_v
        result["WRDHYPnv"] = self.mean_hypernym
        return result
    
    def process_hypernym(self, pos_tagged_corpus):
        """
        Class method to process hypernyms
        
        input:
            pos tagged corpus (nltk)
        """
        lmtzr = WordNetLemmatizer()
        for word,pos in pos_tagged_corpus:
            if pos in NOUN_POS:
        #WRDHYPn	HYNOUNaw	Hypernymy for nouns, mean
                lemma = lmtzr.lemmatize(word)
                #logger.error(lemma)
                try:
                    hypernym_paths = wn.synset(word+'.n.01').hypernym_paths()
                except WordNetError as e:
                    #logger.error("Wordnet fail hyp1: %s" %e)
                    continue
                if hypernym_paths:
                    self.hypernym_n_depth += len(hypernym_paths[0])
                    #WRDHYPnv	HYPm	Hypernymy for nouns and verbs, mean
                    self.hypernym_depth += len(hypernym_paths[0])
                    self.n_count += 1
            elif pos in VERB_POS:
        #WRDHYPv	HYVERBaw	Hypernymy for verbs, mean
                lemma = lmtzr.lemmatize(word, 'v')
                try:
                    hypernym_paths = wn.synset(word + '.v.01').hypernym_paths()
                except WordNetError as e:
                    #logger.error("Wordnet fail hyp2: %s" %e)
                    continue
                if hypernym_paths:
                    self.hypernym_v_depth += len(hypernym_paths[0])
                    #WRDHYPnv	HYPm	Hypernymy for nouns and verbs, mean
                    self.hypernym_depth += len(hypernym_paths[0])
                    self.v_count +=1
            else:
                continue
            

    def process_data(self, tagged_corpus):
        """
        Class method to process raw tagged corpus
        """
        try :
            chunks = self.chunker.parse(tagged_corpus)
        except ValueError as e:
            logger.error("Chunker fail: %s" %e)
            return
        ## loop on all chunks and search for them in wordnet
        for subtree in chunks.subtrees(filter = lambda t: t.label() == 'NP'):
            entity=''
            for word,post in subtree.leaves():
                if word[-1] == '.':
                    entity += "_" + word[:-1]
                    self.add_entity(entity[1:])
                    entity=''
                elif word not in PUNCT:
                    entity += "_" + word
                else:
                    if entity:
                        self.add_entity(entity[1:])
                        entity = ''
            if entity:
                self.add_entity(entity[1:])

    def add_entity(self,entity):
        """
        Add entity to collection
        """
        entity= entity.lower().strip()
        if entity in self.entities:
            new_count,depth = self.entities[entity]
            new_count += 1
            self.entities[entity]=(new_count,depth)
            #print entity, new_count, depth
        else:
            depth = self.get_depth(entity)
            #logger.debug(entity + " " + str(depth))
            if(depth > 0):
                self.entities[entity] = (1, depth)

    def get_avg_depth(self):
        """
        Class method to get average depth ofo wordnet tree
        """
        total_count = 0.0
        total_depth = 0.0
        for key,value in self.entities.iteritems():
            (count,depth) = value #value holds the (Count of entity, its Depth in wordnet)
            #print key , count, depth
            total_count += count
            total_depth += depth * count
        if total_count > 0:    
            return float(total_depth) / float(total_count)
        else:
            return 0
    
    def get_depth(self,word):
        """
        Class method to calculate depth of word in WordNet
        
        !!Only accepts pos tag = NP(Proper Nouns)
        """
        word_synset = wn.synsets(word)
        if word_synset and len(word_synset) > 0:
            return word_synset[0].min_depth() # maximum depth = 16
        else:
            return -1


        
#testing helper functions
def ie_preprocess(document):  #preprocessing should be done externaly 
    sentences = sent_tokenize(document) 
    sentences = [word_tokenize(sent) for sent in sentences] 
    sentences = [pos_tag(sent) for sent in sentences]
    return sentences        

def test():
    # This func for test, and it also show hwo to use this calss
    text ="""'Although is winter and it\xe2\x80\x99s pretty cold outside, the Catalan coast is still one     of the most beautiful places to go. We suggest you to visit it now that there aren\xe2\x80\x99t so many     people crowding the beaches, promenades and bars. It is an excellent opportunity to enjoy in all its splendor     the promenade\xe2\x80\x99s beauty walking\xc2\xa0by the sea with the sun shining and warming you during     this time of the year, and enjoy drinks in the almost empty bars. If you stay in one of our apartments in     Barcelona and you want to go\xc2\xa0away from the city a day or two, the coast of the region of the Maresme     is an excellent choice. We give some suggestions to help you make the most of the\xc2\xa0trip.\nIf you have     a car you have to leave Barcelona direction Girona and deviate in the N-II, you can go on from Montgat to     Matar\xc3\xb3 following the coastal path\xc2\xa0and enjoy the view while driving. Still, it\xe2\x80\x99s     better to catch the train at the nearest station to your home (Plaza Catalunya or Sants Station) as the railway     runs along the coastal line as well and you can enjoy beautiful views throughout the trip. With the train     from Molins de Rei (later its stops at the mentioned stations) to\xc2\xa0Ma\xc3\xa7anet-Massanes,     you\xe2\x80\x99ll get to the places marked on the entire coast of the region of the Maresme.\nThere are     several stops that you can do with the car over this break, but if you go by train you will have to decide     on one of the coastal towns to avoid paying the ticket every time you want to stop in one place. If you     have little time we suggest the closest locations to Barcelona: the Masnou, Premia de Mar and Vilassar de     Mar has beautiful beaches, with promenades full of bars where you can have some beer and tapas, with an old     town that also worth visiting. At Premia de Mar you will find, for example, the Parish of Sant Crist\xc3\xb2fol,     or at Vilassar de Mar the famous bar where Espinaler Salsa was created.\nIf you have more time to make your trip,     you can reach ti\xc2\xa0Matar\xc3\xb3, a town full of\xc2\xa0history where you can visit the Basilica of Santa     Maria, buy sweets at La Confian\xc3\xa7a, surround yourself with nature at the Parc del Montnegre i el Corredor,     etc. If you keep going from Matar\xc3\xb3 there are the most popular beach destinations in summer as\xc2\xa0Arenys     de Mar, Canet de Mar, Sant Pol de Mar, Calella, Pineda de Mar, Santa Susanna and Malgrat de Mar. Probably these     small fishing villages are the nicest you will see in this part of the coast, with beautiful beaches and charming     villages. In Canet you\xe2\x80\x99ll find the Roura House, a modernist building, and the Ateneo Canetense and Museo Casa Lluis Domenech i Montaner, one of the major figures of Catalan Modernism.\nFrom the town of Blanes train enters the interior of Catalonia to the final destination of its journey. If you drive, this trip near Barcelona will take one day and you can choose to take a \xe2\x80\x9cvermouth\xe2\x80\x9d in one place, keep going to have lunch somewhere else, and in the afternoon visit the most attractive monuments that you like the most. Choose a sunny day in winter or autumn to make your little trip and enjoy the beauty of this region!\n'
    """
    sentences = ie_preprocess(text)
    #print sentences
    wordnetanalyzer = WordNetAnalyzer(sentences, True)
    print wordnetanalyzer.get_result()
            
test()

