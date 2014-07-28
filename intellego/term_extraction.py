# -*- coding: utf-8 -*-
import nltk
from lxml import etree
from pattern.en import parsetree as parse_en
from pattern.es import parsetree as parse_es
from pattern.en import tag as tag_en
from pattern.es import tag as tag_es
from pattern.en import pprint as pprint_en
from pattern.es import pprint as pprint_es


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
    for e, k in pairs:
        # eliminate any segments that have non alpha terms and terms which are 1 char long
        if (e.text and len(e.text) > 1) and (k.text and len(k.text) > 1):
            # split the words of the segment into a list. Lowercase all the tokens and elimate any stopwords
            e_token = [w.lower() for w in nltk.word_tokenize(unicode(e.text)) if w.lower() not in stopwords_en]
            k_token = [x.lower() for x in nltk.word_tokenize(unicode(k.text)) if x.lower() not in stopwords_es]
            # add the token list the corpus
            if ''.join(e_token).isalpha() and ''.join(k_token).isalpha():
                if len(e_token) > 0 and len(k_token) > 0:
                    # print e.text, e_token, k_token
                    # if 'articles' in e_token:
                        # print e.text, e_token, k_token
                    corpus.append(nltk.align.AlignedSent(e_token, k_token))
        # count += 1
        # if count > 30:
            # break
    for e, k in pairs:
        # eliminate any segments that have non alpha terms and terms which are 1 char long
        if (e.text and len(e.text) > 1) and (k.text and len(k.text) > 1):
            # split the words of the segment into a list. Lowercase all the tokens and elimate any stopwords
            e_token = [w.lower() for w in nltk.word_tokenize(unicode(e.text)) if w.lower() not in stopwords_en]
            k_token = [x.lower() for x in nltk.word_tokenize(unicode(k.text)) if x.lower() not in stopwords_es]
            # add the token list the corpus
            if ''.join(e_token).isalpha() and ''.join(k_token).isalpha():
                if len(e_token) > 0 and len(k_token) > 0:
                    source_out, target_out = pos_realign(" ".join(e_token), " ".join(k_token))
                    corpus.append(nltk.align.AlignedSent(source_out, target_out))
    # train the aligned corpus to figure out which pairs of words match
    model = nltk.align.IBMModel2(corpus, 2)
    # iterate through the model
    print "%s,%s,%s" % ("source", "target", "precision")
    for k, v in model.probabilities.items():
        # print the term pair if the precision is >=0.5 and not the same string
        if max(v.values()) >= 0.5:
            if k.encode('utf-8') != max(v, key=v.get).encode('utf-8'):
                print "%s,%s,%s" % (k.encode('utf-8'), max(v, key=v.get).encode('utf-8'), max(v.values()))


def pos_realign(source, target):
    source = parse_en(source, relations=True, lemmata=True)
    target = parse_es(target, relations=True, lemmata=True)
    # pprint_en(source)
    # print
    # pprint_es(target)
    pos_en = tag_en(source.string)
    pos_es = tag_es(target.string)
    # print pos_en
    # print pos_es
    pos_realigned = []
    for idx, e in enumerate(pos_en):
        try:
            pos_es.pop(0)
            word_in_target = [word for (word, pos) in pos_es if pos == e[1]]
            # print e, word_in_target
            if word_in_target:
                pos_realigned.append((e[0], word_in_target[0]))
        except:
            break
    source_out = [source for (source, target) in pos_realigned]
    target_out = [target for (source, target) in pos_realigned]
    return source_out, target_out

if __name__ == '__main__':
    main()
    # print pos_realign("Click here to remove all expired articles", "Haga clic aquí para eliminar todos los artículos caducados")
