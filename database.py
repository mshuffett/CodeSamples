#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import logging
import match_keywords

conn = sqlite3.connect('wikipedia.db')


def create_db():
    conn.execute("""
        CREATE TABLE matchdeltas
        (revision_id integer primary key,
        timestamp timestamp,
        page_id integer,
        delta text)
        """)


def create_date_index():
    conn.execute("CREATE INDEX date_index on matchdeltas (timestamp)")


def insert_match_delta(revision, prev_matches, new_matches):
    delta_string = match_keywords.get_match_delta(revision,
                                                  prev_matches,
                                                  new_matches)
    values = (revision['revision_id'],
              revision['revision_timestamp'],
              revision['page_id'],
              delta_string)

    # print values
    with conn:
        conn.execute("""
            insert into matchdeltas(revision_id, timestamp, page_id, delta)
            values (?, ?, ?, ?)""", values)


def reverse_iteritems(iteritems):
    for key, value in iteritems:
        yield value, key


def get_net_deltas():
    id_net = {}
    for id, delta in conn.execute("select revision_id, delta from matchdeltas"):
        id_net[id] = reduce(lambda x, y: x + y, (int(split.split()[0]) for split in delta.strip().split('\n')))
    return id_net


def add_net_deltas(net_deltas):
    iterator = reverse_iteritems(net_deltas.iteritems())
    conn.executemany("update matchdeltas set net = ? where revision_id = ?",
                     iterator)


def main():
    logging.basicConfig(filename='database.log', filemode='w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s')

    create_db()
    match_keywords.load_keywords('single_word_keywords.txt')
    match_keywords.page_change_events(event_handler=insert_match_delta)


if __name__ == "__main__":
    main()
