#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict


def main():
    page_scores = defaultdict(0)
    with open("resources/df_changes.txt") as f, open("resources/daily_df.txt", 'w') as out:
        prev_hour = None
        prev_page_id = None
        for line in f:
            time_string, page_id, score = line.split()
            day_and_hour_string = time_string[:13]

            prev_hour = None


if __name__ == '__main__':
    main()
