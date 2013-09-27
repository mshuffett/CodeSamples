#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from collections import OrderedDict
import tfidf

protest_keywords_file_name = "resources/sorted_ant_word_counts.txt"
non_protest_keywords_file_name = "resources/non_protest_word_counts.txt"
non_protest_max_score = 878542
protest_max_score = 15527
MAX_SCORE = 100 # score to normalize max score to


def load_keywords(file_name):
    d = OrderedDict()
    with open(file_name) as f:
        for line in f:
            s = line.strip().split('\t')
            d[s[0]] = int(s[1])
    return d


def normalize_keywords(d, max):
    scale = MAX_SCORE / max
    for word, count in d.iteritems():
        d[word] = count * scale

def main():
    protest_keywords = load_keywords(protest_keywords_file_name)
    non_protest_keywords = load_keywords(non_protest_keywords_file_name)
    normalize_keywords(protest_keywords, protest_max_score)
    normalize_keywords(non_protest_keywords, non_protest_max_score)
    
    normalized_keywords = OrderedDict()
    for word, count in protest_keywords.iteritems():
        normalized_keywords[word] = count
        
    print protest_keywords.iteritems().next()
    


if __name__ == '__main__':
    main()