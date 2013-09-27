#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math


def bool_tf(document, term):
    return term in document


def idf(total_documents, documents_containing_term):
    return math.log(total_documents / (1 + documents_containing_term))


def tfidf():
    # FIXME
    return bool_tf() * idf()
