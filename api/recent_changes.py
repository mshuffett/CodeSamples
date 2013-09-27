#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'Michael Shuffett'
__email__ = 'mshuffett@gmail.com'

# from datetime import datetime
# from datetime import timedelta
import urllib2
import json
from etool import args, logs, queue, message
import os

log = logs.getLogger('wikipedia_recent_changes')


class API(object):
    """Wikipedia API class"""

    def __init__(self, localization="es"):
        self._url = "http://%s.wikipedia.org/w/api.php" % localization
        self._max_ids = 50

    def get_recent_changes(self, namespace=0):
        """Queries Wikipedia site for the latest changes.

        :param integer namespace: the namespace to restrict to, defaults to 0.
        :returns: a list of changes sorted in reverse chronological order.
        :rtype: list
        """
        url = "%s?action=query&list=recentchanges&format=json&rclimit=max&rcnamespace=%d" % (self._url, namespace)
        try:
            return json.loads(urllib2.urlopen(url).read())["query"]["recentchanges"]
        except Exception:
            log.exception()
            return []

    def get_past_recent_changes(self, start_datetime, end_datetime):
        """Queries Wikipedia for changes that have happened between the two datetimes.

        :param datetime start_datetime: Earliest change datetime.
        :param datetime end_datetime: Latest change datetime.
        :returns: a list of changes sorted in reverse chronological order.
        """
        start_timestamp = start_datetime.isoformat().split('.')[0] + 'Z'
        end_timestamp = end_datetime.isoformat().split('.')[0] + 'Z'
        response = urllib2.urlopen("%s?action=query&list=recentchanges&format=json&rclimit=max&rcend=%s&rcstart=%s" %
                                   (self._url, start_timestamp, end_timestamp))
        try:
            return json.loads(response.read())["query"]["recentchanges"]
        except Exception:
            log.exception()
            return []

    def get_latest_revision(self, rev_ids):
        """returns a list of the latest revisions for the given iterable rev_ids strings"""

        # split list into _max_ids sized chunk
        d = {}
        rev_ids = list(rev_ids)
        for x in xrange(0, len(rev_ids), self._max_ids):
            ids_string = "%7C".join(rev_ids[x:x+self._max_ids])
            response = urllib2.urlopen("%s?action=query&prop=revisions&format=json&rvprop=ids%%7Ctimestamp%%7Ccontent&pageids=%s" % (self._url, ids_string))
            try:
                j = json.loads(response.read())
                if 'warning' in j:
                    pass
                    log.warning(d['warning'])
                for k, v in j['query']['pages'].iteritems():
                    d[k] = v
            except Exception:
                log.exception()
                pass
        return d


def main():
    ap = args.get_parser()
    ap.add_argument('--rev_file', metavar='FILE', type=str, required=False,
                     help='File which stores last revision id.', default="last_rev_file.txt")
    arg = ap.parse_args()
    logs.init(arg)
    log.info("Run Started")

    api = API()
    recent_changes = api.get_recent_changes()

    # Filter to only revisions newer than last run
    last_rev_file = arg.rev_file
    if os.path.exists(last_rev_file):
        with open(last_rev_file) as f:
            last_rev = int(f.read())
            recent_changes = [change for change in recent_changes if change['revid'] > last_rev]

    recently_changed_page_ids = set(str(change['pageid']) for change in recent_changes)
    latest_revisions = api.get_latest_revision(recently_changed_page_ids)
    print(len(latest_revisions))
    print(latest_revisions)
    # TODO actually do something with revisions
    with open(last_rev_file, mode='w') as f:
        f.write(str(max([int(page['revisions'][0]['revid']) for page in latest_revisions.values()])))


if __name__ == "__main__":
    main()
