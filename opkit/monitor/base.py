#!/usr/bin/python
from opkit.utils import common_util as cm_util


class BaseMonitor(object):

    MONITOR_NAME = None

    @classmethod
    def get_subclasses(cls):
        return cm_util.get_subclasses(cls, cm_util.get_package_modules(__package__))


class Check(object):

    @staticmethod
    def check_parts(parts, expect):
        iter_types = (list, tuple, set, frozenset)
        if not isinstance(parts, iter_types):
            raise TypeError("invalid parts type %s" % type(parts))

        if not isinstance(expect, iter_types):
            raise TypeError("invalid expect type %s" % type(expect))

        parts = set(parts)
        if not all([part in expect for part in parts]):
            raise ValueError("invalid parts %s" % parts)
