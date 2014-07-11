# -*- coding: utf-8 -*-
import nltk
from lxml import etree


def main():
    # open the tmx file
    tmx_file = open('../memoire_en-US_es-ES.tmx', 'r')
    # Parse the TMX file into python objects
    tmx_tree = etree.parse(tmx_file)
    # create a list of the "seg" elements, where our segments are contained
    tree = [e for e in tmx_tree.iter("seg")]
    # Pair these segments up and put them into a list
    pairs = zip(tree, tree[1:])[::2]
    corpus = []
    count = 0
    # import the source and target language stopwords
    stopwords_en = nltk.corpus.stopwords.words('english')
    stopwords_es = nltk.corpus.stopwords.words('spanish')
    # iterate through the segment pairs
    for e,k in pairs: 
        # eliminate any segments that have non alpha terms and terms which are 1 char long
        if (e.text and len(e.text)>1) and (k.text and len(k.text)>1):
            # split the words of the segment into a list. Lowercase all the tokens and elimate any stopwords
            e_token = [w.lower() for w in nltk.word_tokenize(unicode(e.text)) if w.lower() not in stopwords_en]
            k_token = [x.lower() for x in nltk.word_tokenize(unicode(k.text)) if x.lower() not in stopwords_es]
            # add the token list the corpus
            if ''.join(e_token).isalpha() and ''.join(k_token).isalpha():
                if len(e_token) > 0 and len(k_token) > 0:
                    # print e.text, e_token, k_token
                    corpus.append(nltk.align.AlignedSent(e_token, k_token))
        # count += 1
        # if count > 30:
            # break
    # train the aligned corpus to figure out which pairs of words match
    model = nltk.align.IBMModel2(corpus,3)
    # iterate through the model
    print "%s,%s,%s" % ("source", "target", "precision")
    for k,v in model.probabilities.items():
        # print the term pair if the precision is >=0.5 and not the same string
        if max(v.values()) >= 0.5:
            if k.encode('utf-8') != max(v, key=v.get).encode('utf-8'):
                print "%s,%s,%s" % (k.encode('utf-8'),max(v, key=v.get).encode('utf-8'), max(v.values()))
if __name__ == '__main__':
    main()
