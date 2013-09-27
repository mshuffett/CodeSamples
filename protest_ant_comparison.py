import revisions
import re
from nltk import SnowballStemmer

NUM_WORDS = 50
found_words = []
stemmer = SnowballStemmer('spanish')


def main():
    with open('sorted_ant_word_counts.txt') as f:
        top_words = []
        for x in xrange(NUM_WORDS):
            top_words.append(f.readline().split()[0])

    curr_page = None
    global found_words
    with open('/Users/shuffett/Workspace/eswiki-20120927-pages-meta-history.xml') as f:
        for revision in revisions.revision_generator(f):
            if revision['page_ns'] != '0' or 'revision_text' not in revision:
                continue

            if curr_page != revision['page_id']:
                prev_rev_text = None
                completed = False
                curr_page = revision['page_id']

            if completed:
                continue

            if revision['revision_text'].find("protest") != -1:
                completed = True
                if prev_rev_text:
                    text = prev_rev_text.lower().strip()
                    new_word_set = set(re.split('\W+', text, flags=re.UNICODE))
                    num_found = 0
                    stemmed_set = set()
                    for word in new_word_set:
                        try:
                            stemmed = stemmer.stem(word)
                            stemmed_set.add(stemmed)
                        except:
                            pass
                    for word in top_words:
                        if word in stemmed_set:
                            num_found += 1
                    found_words.append(num_found)

            else:
                prev_rev_text = revision['revision_text']


if __name__ == '__main__':
    main()
