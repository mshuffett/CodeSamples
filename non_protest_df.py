import revisions
import re
from nltk import SnowballStemmer
from nltk.corpus import stopwords

stemmer = SnowballStemmer('spanish')
stop_set = set(stopwords.words('spanish'))
word_counts = {}


def main():
    curr_page = None
    prev_rev_text = None
    completed = False
    global word_counts

    with open('/Users/shuffett/Workspace/eswiki-20120927-pages-meta-history.xml') as f:
        for revision in revisions.revision_generator(f):
            if revision['page_ns'] != '0' or 'revision_text' not in revision:
                continue

            if curr_page != revision['page_id']:
                if prev_rev_text and not completed:
                    text = prev_rev_text.lower().strip()
                    new_word_set = set(re.split('\W+', text, flags=re.UNICODE))
                    new_word_set.discard('')
                    new_word_set.difference_update(stop_set)
                    for word in new_word_set:
                        try:
                            stemmed = stemmer.stem(word)
                        except:
                            pass
                        else:
                            word_counts[stemmed] = word_counts.get(stemmed, 0) + 1

                completed = False
                curr_page = revision['page_id']

            elif completed:
                continue

            if revision['revision_text'].find("protest") != -1:
                completed = True
            else:
                prev_rev_text = revision['revision_text']


if __name__ == '__main__':
    main()
