from collections import OrderedDict

from opkit.common.constants import Resource
from opkit.monitor.base import BaseMonitor


class Manager(object):
    """ 管理类 """

    __MONITOR = {
        clz.MONITOR_NAME: clz
        for clz in BaseMonitor.get_subclasses()
    }

    def __init__(self, parts=None):
        if parts:
            self._check_parts(parts, self.__MONITOR.keys())
        else:
            parts = self.__MONITOR.keys()

        for part in parts:
            setattr(self, part, self.__MONITOR[part]())

    def _check_parts(self, parts, expect):
        iter_types = (list, tuple, set, frozenset)
        if not isinstance(parts, iter_types):
            raise TypeError("invalid parts type %s" % type(parts))

        if not isinstance(expect, iter_types):
            raise TypeError("invalid expect type %s" % type(expect))

        parts = set(parts)
        if not all([part in expect for part in parts]):
            raise ValueError("invalid parts %s" % parts)

    def usage(self, parts=None):
        if parts:
            self._check_parts(parts, Resource.all_usage_key())
        else:
            parts = Resource.all_usage_key()

        res = OrderedDict()

        for part in parts:
            monitor = getattr(self, part, None)
            if not monitor:
                setattr(self, part, self.__MONITOR[part]())

            usage_fn = getattr(monitor, "usage", None)
            if not usage_fn or not callable(usage_fn):
                # TODO 警告，并跳过
                continue

            res[part] = usage_fn()

        return res





