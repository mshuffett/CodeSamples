import revisions
import sys
import re

rev = revisions.revision_generator(sys.stdin).next()
print re.split('\W+', rev['revision_text'].lower().strip(), flags=re.UNICODE)
