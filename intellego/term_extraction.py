# -*- coding: utf-8 -*-
import nltk
from lxml import etree
from pattern.en import parsetree as parse_en
from pattern.es import parsetree as parse_es
from pattern.en import tag as tag_en
from pattern.es import tag as tag_es
from pattern.en import pprint as pprint_en
from pattern.es import pprint as pprint_es
from align import IBMModel2, AlignedSent
import json
import io
import pdb
import click
from cloud.serialization.cloudpickle import dumps, loads


@click.command()
@click.option('--load', default='ibm2', help="Specifiy a model to save.")
@click.option('--train', help="Train the model. If this flag is not set, then it will load a saved model.", is_flag=True)
@click.option('--debug', help="Print the debug json file. Pipe the output to a file using this flag.", is_flag=True)
@click.option('--csv', help="Print the translated pairs in CSV format. Pipe the output to a file using this flag.", is_flag=True)
def main(load, train):
    if train:
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
            # tuid = el.getparent().getparent().attrib['tuid']
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
                        corpus.append(AlignedSent(e_token, k_token, tuid=e.getparent().getparent().attrib['tuid']))

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
                        corpus.append(AlignedSent(source_out, target_out, tuid=e.getparent().getparent().attrib['tuid']))

        # train the aligned corpus to figure out which pairs of words match
        model = dumps(IBMModel2(corpus, 1))
        with open("models/ibm2.p", "w") as dest:
            dest.write(model)
        result = dumps(corpus)
        with open("models/corpus", "w") as dest:
            dest.write(result)
    else:
        with open("models/ibm2.p") as source:
            result = source.read()
        model = loads(result)
        with open("models/corpus") as source:
            result = source.read()
        corpus = loads(result)
    if csv:
        # iterate through the model
        print "%s,%s,%s" % ("source", "target", "precision")
        for k, v in model.probabilities.items():
            # print the term pair if the precision is >= 0.5 and not the same string
            if max(v.values()) >= 0.5:
                if k.encode('utf-8') != max(v, key=v.get).encode('utf-8'):
                    print "%s,%s,%s" % (k.encode('utf-8'), max(v, key=v.get).encode('utf-8'), max(v.values()))
    # get sent alignments with TUID property
    if debug:
        aligned_corpus = {}
        for sent in corpus:
            aligned = model.align(sent)
            for word in aligned.words:
                v = model.probabilities[word]
                if word not in aligned_corpus:
                    if (max(v.values()) >= 0.4) and max(v, key=v.get):
                        if word.encode('utf-8') != max(v, key=v.get).encode('utf-8'):
                            aligned_corpus[word] = {}
                            aligned_corpus[word]['target'] = max(v, key=v.get).encode('utf-8')
                            aligned_corpus[word]['tuid'] = aligned.tuid
                            aligned_corpus[word]['precision'] = max(v.values())
                            aligned_corpus[word]['source_sent'] = " ".join(aligned.words).encode('utf-8')
                            aligned_corpus[word]['target_sent'] = " ".join(aligned.mots).encode('utf-8')
                            aligned_corpus[word]['alignment'] = str(aligned.alignment)
        print json.dumps(aligned_corpus, indent=4, sort_keys=False)


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
