from collections import OrderedDict

from opkit.common.constants import Resource, Unit
from opkit.kit.base import BaseManager
from opkit.kit.monitor.base import BaseMonitor


class Manager(BaseManager):
    """ 管理类 """

    __MONITOR = {
        clz.MONITOR_NAME: clz
        for clz in BaseMonitor.get_subclasses()
    }

    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)
        for part in self.__MONITOR.keys():
            setattr(self, part, self.__MONITOR[part]())

    def os_usage(self, parts=None):
        if parts:
            self.check_parts(parts, Resource.all_os_usage_key())
        else:
            parts = Resource.all_os_usage_key()

        res = OrderedDict()
        unit = Unit.PERCENT

        for part in parts:
            monitor = getattr(self, part, None)
            if not monitor:
                setattr(self, part, self.__MONITOR[part]())

            usage_fn = getattr(monitor, "usage", None)
            if not usage_fn or not callable(usage_fn):
                continue

            res[Resource.wrap(part, unit)] = usage_fn()

        return res

    def proc_usage(self, pid=None, proc_name=None, parts=None):
        u""" 查询进程使用率 """
        return self.proc(
            proc_method='usage',
            pid=pid,
            proc_name=proc_name,
            parts=parts
        )

    def proc_info(self, pid=None, proc_name=None, parts=None):
        u""" 查询进程信息 """
        return self.proc(
            proc_method='info',
            pid=pid,
            proc_name=proc_name,
            parts=parts
        )

    def proc(self, proc_method, pid=None, proc_name=None, parts=None):
        if parts and proc_method == 'usage':
            self.check_parts(parts, Resource.all_proc_usage_key())

        proc_monitor = getattr(self, Resource.PROC.value, None)
        if not proc_monitor:
            setattr(self, Resource.PROC.value,
                    self.__MONITOR[Resource.PROC.value])

        method = getattr(proc_monitor, proc_method, None)
        if not callable(method):
            return OrderedDict()

        return self._wrap_data(
            method(pid=pid, proc_name=proc_name, parts=parts),
            Unit.PERCENT
        )

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

    @staticmethod
    def _wrap_data(data, unit):
        cp_data = data.copy()
        for key, val in cp_data.items():
            if key in Resource.all_proc_usage_key():
                data.pop(key)
                data[Resource.wrap(key, unit)] = val

        return data
