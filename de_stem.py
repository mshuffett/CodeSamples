import revisions
import re
from nltk import SnowballStemmer

NUM_WORDS = 50
stemmer = SnowballStemmer('spanish')
stem_to_word = {}
XML_PATH = '/Users/shuffett/Workspace/eswiki-20120927-pages-meta-history.xml'


def main():
    global stem_to_word
    with open('sorted_ant_word_counts.txt') as f:
        top_words = []
        for x in xrange(NUM_WORDS):
            word = f.readline().split()[0]
            top_words.append(word)
            stem_to_word[word] = set()

    curr_page = None
    global word_dict
    with open(XML_PATH) as f:
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
                    for word in new_word_set:
                        try:
                            stemmed = stemmer.stem(word)
                            if stemmed in top_words:
                                stem_to_word[stemmed].add(word)
                        except:
                            pass

            else:
                prev_rev_text = revision['revision_text']


if __name__ == '__main__':
    main()
