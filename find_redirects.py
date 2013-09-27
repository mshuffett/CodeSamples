import revisions
import sys

for rev in revisions.revision_generator(sys.stdin):
    if rev.has_key('page_redirect'):
        print 'page redirect'
        print rev