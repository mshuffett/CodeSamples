#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from datetime import date, timedelta

conn = sqlite3.connect('wikipedia.db')


def get_keyword_count(start_iso, end_iso):
    keywords = 0
    for delta, in conn.execute("""
            SELECT delta FROM matchdeltas
            WHERE timestamp > ? AND timestamp < ?""",
            (start_iso, end_iso)):
        for split in delta.strip().split('\n'):
            num, word = split.split()
            keywords += int(num)
    return keywords


def create_weeks():
    conn.execute("""
        CREATE TABLE weeks
        (start timestamp primary key,
        end timestamp,
        count integer)
        """)


def populate_weeks(start_iso, end_iso):
    conn.execute("INSERT INTO WEEKS VALUES (?, ?, ?)",
                 (start_iso, end_iso, get_keyword_count(start_iso, end_iso)))


def populate_days(start_iso, end_iso):
    conn.execute("INSERT INTO days VALUES (?, ?, ?)",
                 (start_iso, end_iso, get_keyword_count(start_iso, end_iso)))


def populate_week_revisions(start_iso, end_iso):
    conn.execute("""
        INSERT INTO week_revisions
        VALUES (?, ?,
        (SELECT count(*) FROM matchdeltas
        WHERE timestamp > ? AND timestamp < ?))""",
        (start_iso, end_iso, start_iso, end_iso))


def create_days():
    conn.execute("""
        CREATE TABLE days
        (start timestamp primary key,
        end timestamp,
        count integer)
        """)


def populate_day_revisions(start_iso, end_iso):
    conn.execute("""
        INSERT INTO day_revisions
        VALUES (?, ?,
        (SELECT count(*) FROM matchdeltas
        WHERE timestamp > ? AND timestamp < ?))""",
        (start_iso, end_iso, start_iso, end_iso))


def date_gen(start_date=date(2011, 1, 1),
             final_date=date(2012, 9, 27),
             delta=timedelta(days=7)):
    """Generator for given timedelta and time range.
    Return tuple (start, end) where start and end are in iso strings and are
    seperated by delta.

    Keyword arguments:
    start_date -- the first date (default date(2011, 1, 1))
    final_date -- the last date (default date(2012, 9, 27))
    delta -- the time_delta between the times (default timedelta(days=7))

    """
    while True:
        end = start_date + delta
        start_iso = start_date.isoformat()
        end_iso = end.isoformat()
        yield (start_iso, end_iso)
        if end > final_date:
            break
        start_date = end


def add_page_correlation(page_dict, matrix):
    sorted_words = [key for key in page_dict.keys() if page_dict[key] > 0]
    if len(sorted_words <= 1):
        return
    sorted_words.sort()
    for i in xrange(len(sorted_words) - 1):
        for j in xrange(1 + i, len(sorted_words)):
            new_value = matrix.get((sorted_words[i], sorted_words[j]), 0) + 1
            matrix[(sorted_words[i], sorted_words[j])] = new_value


def get_page_pairs(page_dict):
    pairs = []
    sorted_words = [key for key in page_dict.keys() if page_dict[key] > 0]
    if len(sorted_words) <= 1:
        return pairs
    sorted_words.sort()
    for i in xrange(len(sorted_words) - 1):
        for j in xrange(1 + i, len(sorted_words)):
            pairs.append((sorted_words[i], sorted_words[j]))
    return pairs


def add_date_correlations(start, end, matrix):
    current_page_id = None
    date_set = set()
    page_dict = None
    for page_id, delta in conn.execute("""
            SELECT page_id, delta FROM matchdeltas
            WHERE timestamp > ? AND timestamp < ?
            ORDER BY page_id""", (start, end)):
        if current_page_id != page_id:
            if current_page_id:
                date_set.update(get_page_pairs(page_dict))
            page_dict = {}
            current_page_id = page_id
        for split in delta.strip().split('\n'):
            num, word = split.split()
            num = int(num)
            page_dict[word] = page_dict.get(word, 0) + num
    for pair in date_set:
        matrix[pair] = matrix.get(pair, 0) + 1


def date_task(fn,
              start_date=date(2011, 1, 1),
              final_date=date(2012, 9, 27),
              delta=timedelta(days=7)):
    while True:
        end = start_date + delta
        start_iso = start_date.isoformat()
        end_iso = end.isoformat()
        fn(start_iso, end_iso)
        if end > final_date:
            break
        start_date = end


def main():
    # create_days()
    # date_task(populate_days, delta=timedelta(days=1))
    # conn.commit()
    global matrix
    matrix = {}
    fn = lambda start, end: add_date_correlations(start, end, matrix)
    date_task(fn, delta=timedelta(days=1))
    # for start, end in week_gen():
        # add_week_correlations(start, end, matrix)
        # insert_into_db(start, end)
    # conn.commit()


if __name__ == "__main__":
    main()
