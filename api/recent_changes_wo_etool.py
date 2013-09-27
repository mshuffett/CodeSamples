#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'Michael Shuffett'
__email__ = 'mshuffett@gmail.com'

from datetime import datetime
from datetime import timedelta
import urllib2
import json
# from etool import args, logs, queue, message

# log = logs.getLogger('wikipedia_recent_changes')
url = "http://es.wikipedia.org/w/api.php?action=query&list=recentchanges&format=json&rclimit=max"


def get_recent_changes():
    """queries the wikipedia site for the latest changes.

    returns a list of changes sorted in reverse chronological order.
    """
    try:
        return json.loads(urllib2.urlopen(url).read())["query"]["recentchanges"]
    except Exception:
        # log.exception()
        return []


def get_past_recent_changes(start_datetime, end_datetime):
    """queries the wikipedia site for changes that have happened between the two
    timestamps.

    returns a list of changes sorted in reverse chronological order.
    """
    start_timestamp = start_datetime.isoformat().split('.')[0] + 'Z'
    end_timestamp = end_datetime.isoformat().split('.')[0] + 'Z'
    response = urllib2.urlopen("%s&rcend=%s&rcstart=%s" % (url, start_timestamp, end_timestamp))
    try:
        return json.loads(response.read())["query"]["recentchanges"]
    except Exception:
        # log.exception()
        return []


def get_last_revid():
    """returns the latest revid from a previous run"""
    pass  # TODO


def save_revisions(revisions):
    """takes revisions in json text form and saves them to s3"""
    pass  # TODO


def main():
    # ap = args.get_parser()
    # ap.add_argument('--my-arg', metavar='MY_ARG', type=str, required=False,
    #                 help='An extra argument I want to add.')
    # arg = ap.parse_args()
    # logs.init(arg)
    changes = get_recent_changes()
    last_revid = get_last_revid()
    page_to_earliest_rev = {}  # dictionary mapping pageid to earliest new revision
    url = 'http://es.wikipedia.org/w/api.php?action=query&prop=revisions&format=json&rvprop=ids%7Ctimestamp%7Ccontent&rvlimit=max'
    for change in changes:
        if change['revid'] <= last_revid:
            break
        if 'ns' != 0:
            continue
        page_to_earliest_rev[change['pageid']] = change['revid']

    for pageid, revid in page_to_earliest_rev.iteritems():
        url_with_params = url + '&rvendid=%d&pageids=%d' % (revid, pageid)
        try:
            save_revisions(urllib2.urlopen(url_with_params).read())
        except Exception:
            log.exception()


if __name__ == "__main__":
    main()
