#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import codecs
# import xml.etree.ElementTree as ET
import xml.etree.cElementTree as ET


def basetag(tag):
    if tag:
        nc = re.match(r'([^}]+})(\w+)', tag)
        if nc:
            return nc.group(1), nc.group(2)

    return None, tag

stdout_utf8 = codecs.getwriter('utf8')(sys.stdout)


def print_revision(revision):
    stdout_utf8.write(str(revision))
    stdout_utf8.write('\n')


def print_revision_text(revision):
    stdout_utf8.write(revision.get('revision_text', ''))
    # stdout_utf8.write(revision.get('revision_id', ''))
    # stdout_utf8.write(revision.get('page_id', ''))
    stdout_utf8.write('\n')


def revision_generator(stream, revisions=0, pages=0):
    """Generator for stream parsed as Wikipedia edit XML"""
    assert stream, "Need a valid input stream to parse"

    # p = ET.iterparse(stream, events=['start', 'end'])
    p = ET.iterparse(stream, events=('start', 'end'))
    in_page = False
    in_revision = False
    page_info = {}
    revision_info = {}
    path = []
    if pages == 0:
        pages -= 1
    for evt, ele in p:
        n = basetag(ele.tag)[1]
        #print evt, n, ' page=', in_page, ' revision=', in_revision
        if evt == 'start' and n == 'page':
            if pages == 0:
                break
            pages -= 1
            in_page = True
            in_revision = False
            page_info = {}

        if evt == 'start' and n == 'revision':
            in_page = False
            in_revision = True
            revision_info = page_info.copy()
            path = []

        if evt == 'start' and in_revision:
            path.append(basetag(ele.tag)[1])

        if in_page and evt == 'end':
            if ele.text:
                page_info['page_' + n] = ele.text.strip()

        if in_revision and evt == 'end':
            if ele.text and ele.text.strip():
                revision_info['_'.join(path)] = ele.text.strip()

            if path:
                path.pop()

        if evt == 'end' and n == 'revision':
            ele.clear()
            yield revision_info
            revisions -= 1
            if revisions == 0:
                break


def shred_document(stream, output_fn=print_revision, revisions=0):
    """Parse stream as Wikipedia edit XML and call output_fn with each revision.
    Limit number of revisions to revisions where starting value of 0 or less is unlimited.
    """
    assert stream, "Need a valid input stream to parse"
    for rev in revision_generator(stream, revisions):
        output_fn(rev)


def shred_document_without_gen(stream, output_fn=print_revision):
    """Parse stream as Wikipedia edit XML and call output_fn with each revision."""
    assert stream, "Need a valid input stream to parse"

    # p = ET.iterparse(stream, events=['start', 'end'])
    p = ET.iterparse(stream, events=('start', 'end'))
    in_page = False
    in_revision = False
    page_info = {}
    revision_info = {}
    path = []
    for evt, ele in p:
        n = basetag(ele.tag)[1]
        #print evt, n, ' page=', in_page, ' revision=', in_revision
        if evt == 'start' and n == 'page':
            in_page = True
            in_revision = False
            page_info = {}

        if evt == 'start' and n == 'revision':
            in_page = False
            in_revision = True
            revision_info = page_info.copy()
            path = []

        if evt == 'start' and in_revision:
            path.append(basetag(ele.tag)[1])

        if in_page and evt == 'end':
            if ele.text:
                page_info['page_' + n] = ele.text.strip()

        if in_revision and evt == 'end':
            if ele.text and ele.text.strip():
                revision_info['_'.join(path)] = ele.text.strip()

            if path:
                path.pop()

        if evt == 'end' and n == 'revision':
            output_fn(revision_info)
            ele.clear()


def main():
    print ''
    shred_document(sys.stdin, revisions=3, output_fn=print_revision_text)


if __name__ == "__main__":
    main()
