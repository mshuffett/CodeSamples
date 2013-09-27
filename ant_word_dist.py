#!/usr/bin/env python
# -*- coding: utf-8 -*-

import revisions
import re
from nltk import SnowballStemmer
from nltk.corpus import stopwords

curr_page = None
completed = False
prev_rev_text = None
word_counts = {}
stop_set = set(stopwords.words('spanish'))
stemmer = SnowballStemmer('spanish')


def prev_protest(revision):
    if revision['page_ns'] != '0' or 'revision_text' not in revision:
        return

    global curr_page
    if curr_page != revision['page_id']:
        global completed
        global prev_rev_text
        prev_rev_text = None
        completed = False
        curr_page = revision['page_id']

    if completed:
        return

    if revision['revision_text'].find("protest") != -1:
        completed = True
        if prev_rev_text:
            text = prev_rev_text.lower().strip()
            new_word_set = set(re.split('\W+', text, flags=re.UNICODE))
            new_word_set.discard('')
            new_word_set.difference_update(stop_set)
            global word_counts
            for word in new_word_set:
                try:
                    stemmed = stemmer.stem(word)
                except:
                    pass
                else:
                    word_counts[stemmed] = word_counts.get(stemmed, 0) + 1

    else:
        prev_rev_text = revision['revision_text']


def main():
    with open('/Users/shuffett/Workspace/eswiki-20120927-pages-meta-history.xml') as f:
        revisions.shred_document_without_gen(f, output_fn=prev_protest)
        # revisions.shred_document(f, revisions=10000, output_fn=prev_protest)


if __name__ == '__main__':
    main()
