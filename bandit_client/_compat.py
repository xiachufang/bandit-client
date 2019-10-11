# coding: utf-8

from __future__ import absolute_import

import six


def utf8(value):
    if isinstance(value, (six.binary_type, type(None))):
        return value

    return str(value).encode("utf-8")


def to_unicode(value):
    if isinstance(value, (six.text_type, type(None))):
        return value

    if not isinstance(value, six.text_type):
        raise TypeError("text type required.")

    return value.decode("utf-8")
