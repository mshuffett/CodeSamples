#!/usr/bin/env python

import bz2
import re
import pdb
import signal

import revisions
from nltk import SnowballStemmer


def int_handler(signal, frame):
    pdb.set_trace()


keyword_file = 'normalized_keywords.txt'
stemmer = SnowballStemmer('spanish')
file_name = '/home/michael/Desktop/eswiki-latest-pages-meta-history.xml.bz2'
f = bz2.BZ2File(file_name, buffering=(2 << 16) + 8)
revision_generator = revisions.revision_generator(f)
keyword_scores = {}

with open(keyword_file) as f:
    for line in f:
        score, word = line.strip().split('\t')
        keyword_scores[word] = float(score)


def score(text):
    words = set()
    for word in re.split('\W+', text.lower().strip(), flags=re.UNICODE):
        # stemmer ocassionally raises an exception on certain words
        try:
            words.add(stemmer.stem(word))
        except:
            pass
    # FIXME: reduce on smaller set
    return reduce(lambda x, y: x + y, (keyword_scores.get(word, 0) for word in words))


def main():
    found = None
    last_page = None
    last_score = None

    with open('resources/first_protest.txt', 'w') as f:
        with open('resources/df_changes.txt', 'w') as df:
            for revision in revision_generator:
                if revision['page_ns'] != '0' or 'revision_text' not in revision:
                    continue
                if found:
                    if revision['page_id'] == last_page:
                        continue
                    found = False
                if revision['revision_text'].find("protest") != -1:
                    f.write(revision['revision_timestamp'] + '\n')
                    found = True
                else:
                    s = score(revision['revision_text'])
                    # FIXME: potential issue if score was greater than 0 then decreased to 0
                    if s != 0 and (s != last_score or revision['page_id'] != last_page):
                        df.write('%s\t%s\t%f\n' % (revision['revision_timestamp'], revision['page_id'], s))
                        last_score = s
                last_page = revision['page_id']

if __name__ == '__main__':
    signal.signal(signal.SIGINT, int_handler)
    main()
