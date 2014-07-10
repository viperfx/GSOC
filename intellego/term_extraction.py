# -*- coding: utf-8 -*-
import nltk
from lxml import etree


def main():
    tmx_file = open('../memoire_en-US_es-ES.tmx', 'r')
    tmx_tree = etree.parse(tmx_file)
    # tree = [nltk.word_tokenize(unicode(e.text)) for e in tmx_tree.iter("seg") if e.text and len(e.text) > 1]
    # tree = [e for e in tree if len(e) > 0]
    # pairs = zip(tree, tree[1:])[::2]
    # print pairs[:10]
    tree = [e for e in tmx_tree.iter("seg")]
    pairs = zip(tree, tree[1:])[::2]
    corpus = []
    count = 0
    for e,k in pairs: 
        if (e.text and e.text.isalpha() and len(e.text)>1) and (k.text and k.text.isalpha() and len(k.text)>1):
            e_token = nltk.word_tokenize(unicode(e.text))
            k_token = nltk.word_tokenize(unicode(k.text))
            # print e_token, k_token, nltk.pos_tag(e_token), nltk.pos_tag(k_token)
            if len(e_token) > 0 and len(k_token) > 0:
                corpus.append(nltk.align.AlignedSent(e_token, k_token))
            # count += 1
            # if count > 1000:
                # break
    model = nltk.align.IBMModel2(corpus,3)
    # print model.align(corpus[1])
    for k,v in model.probabilities.items():
        if max(v.values()) >= 0.5 and k.encode('utf-8') != max(v, key=v.get).encode('utf-8'):
            print k.encode('utf-8'),max(v, key=v.get).encode('utf-8'), max(v.values())
if __name__ == '__main__':
    main()
