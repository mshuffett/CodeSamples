#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from datetime import date, timedelta
# import json

conn = sqlite3.connect('wikipedia.db')


def create_db():
    conn.execute("""
        CREATE TABLE weeks
        (start timestamp primary key,
        end timestamp,
        count integer)
        """)


def insert_into_db(start_iso, end_iso):
    conn.execute("""
            INSERT INTO weeks
            VALUES (?, ?,
            (SELECT count(*) FROM matchdeltas WHERE timestamp > ? AND timestamp < ?))""",
            (start_iso, end_iso, start_iso, end_iso))


def week_gen():
    final_date = date(2012, 9, 28)  # one day after last date of data
    start = date(2011, 1, 1)  # start date given by naren
    while True:
        end = start + timedelta(days=7)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        yield (start_iso, end_iso)
        if end >= final_date:
            break
        start = end


def add_page_correlation(page_dict, matrix):
    sorted_words = [key for key in page_dict.keys() if page_dict[key] > 0]
    if len(sorted_words <= 1):
        return
    sorted_words.sort()
    for i in xrange(len(sorted_words) - 1):
        for j in xrange(1 + i, len(sorted_words)):
            matrix[(sorted_words[i], sorted_words[j])] = matrix.get((sorted_words[i], sorted_words[j]), 0) + 1


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


def add_week_correlations(start, end, matrix):
    current_page_id = None
    week_set = set()
    page_dict = None
    for page_id, delta in conn.execute("""
            SELECT page_id, delta FROM matchdeltas
            WHERE timestamp > ? AND timestamp < ?
            ORDER BY page_id""", (start, end)):
        if current_page_id != page_id:
            if current_page_id:
                week_set.update(get_page_pairs(page_dict))
            page_dict = {}
            current_page_id = page_id
        for split in delta.strip().split('\n'):
            num, word = split.split()
            num = int(num)
            page_dict[word] = page_dict.get(word, 0) + num
    for pair in week_set:
        matrix[pair] = matrix.get(pair, 0) + 1


def weekly_task(fn=insert_into_db):
    final_date = date(2012, 9, 28)  # one day after last date of data
    start = date(2011, 1, 1)  # start date given by naren
    while True:
        end = start + timedelta(days=7)
        start_iso = start.isoformat()
        end_iso = end.isoformat()
        insert_into_db(start_iso, end_iso)
        if end >= final_date:
            break
        start = end


def main():
    global matrix
    matrix = {}
    for start, end in week_gen():
        add_week_correlations(start, end, matrix)
        # insert_into_db(start, end)
    # with open('correlations.json', 'w') as f:
    #     json.dump(matrix, f)
    # conn.commit()


if __name__ == "__main__":
    main()
