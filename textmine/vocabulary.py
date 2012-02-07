import subprocess
import codecs
from HTMLParser import HTMLParser

class Stemmer(object):
    
    _path_to_util = None
    
    def __init__(self, path_to_util):
        self._path_to_util = path_to_util
        
    def stem_text(self, words):
        prog_input = " ".join(words)
        stemmer_proc = subprocess.Popen([self._path_to_util, '-nl', '-e', 'utf-8'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = stemmer_proc.communicate(prog_input)
        out_words = [unicode(word.split('|')[0].split('?')[0].strip('\r')) for word in output[0].split('\n') if len(word) > 0]
        return out_words
    
class InitialParser(HTMLParser):
    
    def __init__(self):
        self.refresh()
        
    def refresh(self):
        self.reset()
        self.fed = []
        
    def handle_data(self, d):
        self.fed.append(d)
        
    def get_data(self):
        return ''.join(self.fed)
    
    def parse(self, text):
        self.refresh()
        self.feed(text)
        parsed = self.get_data()
        words = [word.lower().strip(".,:'\"-!?%$+=1234567890") for word in parsed.split(" ")]
        words = [w for w in words if len(w) > 1]
        final_words = []
        for w in words:
            index = 0
            start_index = 0
            reading_word = False
            w = w + " "
            for ch in w:
                good_symbol = (ord(ch) >= 97 and ord(ch) <= 122) or (ord(ch) >= 1072 and ord(ch) <= 1105)
                if reading_word:
                    if not good_symbol:
                        reading_word = False
                        if index - start_index > 1:
                            final_words.append(w[start_index:index])
                else:
                    if good_symbol:
                        reading_word = True
                        start_index = index  
                index += 1       
        #print " ".join(words)
        #print " ".join(final_words)     
        return final_words
            
class StopWordsFilter(object):
    
    _bad_words = None
    
    def __init__(self, stop_words_in, stemmer, parser):
        self.make_list(stemmer, parser, stop_words_in)
        
    def make_list(self, stemmer, parser, stop_words_in):
        text = codecs.open(stop_words_in, encoding='utf-8', mode='r').read()
        self._bad_words = {w: True for w in stemmer.stem_text(parser.parse(text))}
    
    def cleanse(self, words):
        return [w for w in words if not w in self._bad_words]
    
class VocabularyTransform(object):
    
    _stemmer = None
    _filters = None
    _initial_parser = None
    _vocabulary = None
    _corpus = None
    
    @staticmethod
    def make(path_to_stemmer, stop_words_in):
        stemmer = Stemmer(path_to_stemmer)
        parser = InitialParser()
        filters = [StopWordsFilter(stop_words_in, stemmer, parser)]
        return VocabularyTransform(parser, stemmer, filters)
    
    def __init__(self, initial_parser, stemmer, filters):
        self._stemmer = stemmer
        self._filters = filters
        self._initial_parser = initial_parser
        
    def create_from_texts(self, documents):
        (vocabulary, cleansed_documents) = self.stem_and_cleanse_texts(documents)
        self.rank_features(vocabulary, cleansed_documents)
        self._vocabulary = self.select_features(vocabulary)
        self._corpus = self.select_documents(self._vocabulary, cleansed_documents)
        self.weight_words(vocabulary, self._corpus)
        return (self._vocabulary, self._corpus)
           
    def rank_features(self, vocabulary, docs):
        VocabularyTransform.idf(vocabulary, docs)
    
    def select_features(self, vocabulary):
        return VocabularyTransform.default_selector(vocabulary)
    
    def select_documents(self, vocabulary, docs):
        words = {w[0]: True for w in vocabulary}
        cleansed = []
        for doc in docs:
            remaining = {word: value for word, value in doc.iteritems() if word in words}
            if len(remaining.keys()) > 0:
                cleansed.append(remaining)
        return cleansed
    
    def weight_words(self, vocabulary, docs):
        for d in docs:
            VocabularyTransform.boolean_transform(d)
        
    def stem_and_cleanse_texts(self, texts):
        arrays = [self._initial_parser.parse(t) for t in texts]
        all_words = [item for sublist in arrays for item in sublist]
        stemmed_words = self._stemmer.stem_text(all_words)
        if len(all_words) != len(stemmed_words):
            raise Exception("Something is wrong with parsing")
        stemmed_texts = []
        cur_sum = 0
        for a in arrays:
            stemmed_texts.append(stemmed_words[cur_sum : cur_sum + len(a)])
            cur_sum += len(a)
        for index, st in enumerate(stemmed_texts):
            for f in self._filters:
                cleansed_list = f.cleanse(st)
                cleansed_dict = {}
                for w in cleansed_list:
                    if not w in cleansed_dict:
                        cleansed_dict[w] = 0
                    cleansed_dict[w] += 1
                stemmed_texts[index] = cleansed_dict
                #print stemmed_texts[index]
        stemmed_texts = [st for st in stemmed_texts if len(st.keys()) > 0]
        vocabulary = {item: 0 for sublist in stemmed_texts for item in sublist}
        print "total words after initial cleansing: " + str(len(vocabulary.keys()))
        return (vocabulary, stemmed_texts)
    
    # words vector values transformations
    @staticmethod
    def boolean_transform(words):
        for k in words.keys():
            words[k] = 1
        return words
    
    # feature ranking metrics
    @staticmethod
    def idf(vocabulary, documents):
        docs_len = len(documents)
        for word in vocabulary.keys():
            count = 0
            for d in documents:
                if word in d:
                    count += 1
            vocabulary[word] = float(count) / docs_len
            
    # feature selecting
    @staticmethod
    def default_selector(vocabulary):
        items = vocabulary.items()
        items.sort(key=lambda v: v[1])
        items = [item for item in items if item[1] < 0.5]
        l = len(items)
        if l > 1000:
            items = items[l - 1000 : l]
        return items
        
        