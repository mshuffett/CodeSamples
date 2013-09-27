#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nltk.corpus import movie_reviews
import random
import nltk
import logging
import revisions
import re
from nltk import SnowballStemmer
from nltk.corpus import stopwords
import sys
import cPickle as pickle
import bz2
import os
import shelve


NUM_FEATURES = 2000
stemmer = SnowballStemmer('spanish')
stop_set = set(stopwords.words('spanish'))


def load_top_words(num):
    words = []
    with open('resources/sorted_ant_word_counts.txt') as f:
        for x in xrange(num):
            words.append(f.readline().split('\t')[0])
    return words

documents = [(list(movie_reviews.words(fileid)), category)
    for category in movie_reviews.categories()
    for fileid in movie_reviews.fileids(category)]
random.shuffle(documents)

# Natural Language Toolkit: code_document_classify_fd

all_words = nltk.FreqDist(w.lower() for w in movie_reviews.words())
word_features = all_words.keys()[:2000]  # [_document-classify-all-words]


def document_features(document_word_set, word_features):
    # document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_word_set)
    return features


def get_stemmed_word_list(text):
    words = []
    for word in re.split('\W+', text.lower().strip(), flags=re.UNICODE):
        # stemmer ocassionally raises an exception on certain words
        try:
            words.append(stemmer.stem(word))
        except:
            logging.exception("Stemming exception with word %s" % word)
    return words


def get_stemmed_word_set(text):
    words = set()
    for word in re.split('\W+', text.lower().strip(), flags=re.UNICODE):
        # stemmer ocassionally raises an exception on certain words
        try:
            words.add(stemmer.stem(word))
        except:
            logging.exception("Stemming exception with word %s" % word)
    return words


def categorized_page_gen(generator):
    page_num = 0
    curr_page = None
    completed = True  # start as true to bypass writing a non-protest revision
    prev_rev_text = None

    for revision in generator:
            if revision['page_ns'] != '0' or 'revision_text' not in revision:
                continue

            if curr_page != revision['page_id']:
                logging.info("Processed %d page." % page_num)
                page_num += 1
                if not completed and prev_rev_text:  # means that the prev page was a non-protest
                    yield (get_stemmed_word_set(prev_rev_text), 'non-protest')
                prev_rev_text = None
                completed = False
                curr_page = revision['page_id']

            if completed:
                continue

            if revision['revision_text'].find("protest") != -1:
                completed = True
                if prev_rev_text:
                    yield (get_stemmed_word_set(prev_rev_text), 'protest')

            else:
                prev_rev_text = revision['revision_text']

    if not completed and prev_rev_text:  # means that the last page was a non-protest
        yield (get_stemmed_word_set(prev_rev_text), 'non-protest')


def train_set_gen(page_generator, shelf, word_features):
    """Randomly yields approximately 90% of the training data and adds the other 10% to test_set"""
    added = 0
    for words, category in page_generator:
        rand = random.randint(1, 10)  # random int to choose approximately 10% test set iteratively
        featureset = (document_features(words, word_features), category)
        if rand == 10:
            shelf[str(added)] = featureset
            added += 1
            logging.info("Added test item %d" % added)
        else:
            yield featureset


def main():
    logging.basicConfig(filename='resources/categorization.log', filemode='w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s')
    logging.info("Run Started")
    try:
        word_features = load_top_words(NUM_FEATURES)
        file_name = '/home/michael/Desktop/eswiki-latest-pages-meta-history.xml.bz2'
        if os.path.isfile(file_name):
            logging.info('BZ2 file found.')
            f = bz2.BZ2File(file_name, buffering=(2<<16) + 8)
        else:
            f = sys.stdin
        shelf = shelve.open('resources/shelf', protocol=2)
        revision_generator = revisions.revision_generator(f)
        page_generator = categorized_page_gen(revision_generator)
        train_set_generator = train_set_gen(page_generator, shelf, word_features)
        classifier = nltk.NaiveBayesClassifier.train(train_set_generator)
        logging.info("Finished Training")
        shelf.close()
        logging.info('Shelf Closed.')
        shelf = shelve.open('resources/shelf', protocol=2)
        logging.info(nltk.classify.accuracy(classifier, shelf.itervalues()))
        logging.info("Most Informative Features\n%s" % classifier.most_informative_features())
        shelf.close()
        f.close()
        logging.info('Starting classifier pickle')
        with open('classifier.pkl', 'wb') as f:
            pickle.dump(classifier, f, protocol=pickle.HIGHEST_PROTOCOL)
        logging.info('Classifier pickled')
    except:
        logging.exception('Exception')

if __name__ == '__main__':
    main()
