#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import revisions
import codecs
import logging

# keywords = frozenset(['movement', 'ideas', 'society', 'computer', 'protest', 'government', 'strike'])
keywords = frozenset((u'patrón', u'acción', u'campaña', u'aquí', u'día', u'discusión'))
join_char = '\t'  # use \001 for Hive tables
pattern = re.compile('\W+', flags=re.UNICODE)
stdout_utf8 = codecs.getwriter('utf8')(sys.stdout)


def match_keywords(revision):
    print_revision_matches(revision, revision_keywords(revision))


def print_revision_matches(revision, matches):
    for (k, c) in matches.items():
        stdout_utf8.write(join_char.join([k, str(c),
                          revision.get('revision_timestamp', ''),
                          revision.get('revision_id', ''),
                          revision.get('revision_parentid', ''),
                          revision.get('revision_contributor_username', ''),
                          revision.get('page_title', ''),
                          revision.get('page_id', '')]) + '\n')


def revision_keywords(revision):
    """Returns a dictionary of found keywords mapped to the times found for a revision."""
    try:
        matches = {}
        for t in re.split(pattern, revision.get('revision_text', '')):
            l = t.lower()
            if l in keywords:
                matches[l] = 1 + matches.get(l, 0)

        return matches

    except Exception as e:
        sys.stderr.write('Exception %s\n' % e)


def get_match_delta(revision, prev_matches, new_matches):
    key_set = set(word for word in new_matches.keys())
    for word in prev_matches.keys():
        key_set.add(word)

    changes = []
    for word in key_set:
        change = new_matches.get(word, 0) - prev_matches.get(word, 0)
        if change != 0:
            changes.append("%+d %s\n" % (change, word))

    return ''.join(changes)


def print_match_delta(revision, prev_matches, new_matches):
    stdout_utf8.write(get_match_delta(revision, prev_matches, new_matches))


def page_change_events(iterations=0, event_handler=print_match_delta, pages=0):
    page_id = None
    parsed = 0
    for rev in revisions.revision_generator(sys.stdin, revisions=iterations, pages=pages):
        parsed += 1
        if rev.get('page_id', '') != page_id:
            current_matches = {}
            page_id = rev.get('page_id', '')
        matches = revision_keywords(rev)
        if matches != current_matches:
            logging.info("Event found on revision %d" % parsed)
            event_handler(rev, current_matches, matches)
            current_matches = matches
            # print current_matches
        # print_revision_matches(rev, matches)


def load_keywords(filename):
    """Loads keywords from a file containing one keyword per line as utf-8."""
    with open(filename) as f:
        global keywords
        keywords = frozenset([unicode(word, encoding='utf8').strip() for word in f])


def main():
    print ''
    # revisions.shred_document(sys.stdin, output_fn=revision_keywords, revisions=10)
    page_change_events(iterations=1000)
    print ''


if __name__ == "__main__":
    main()
