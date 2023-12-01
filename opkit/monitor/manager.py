from collections import OrderedDict

from opkit.common.constants import Resource
from opkit.monitor.base import (
    BaseMonitor,
    Check
)


class Manager(Check):
    """ 管理类 """

    __MONITOR = {
        clz.MONITOR_NAME: clz
        for clz in BaseMonitor.get_subclasses()
    }

    def __init__(self, parts=None):
        if parts:
            self.check_parts(parts, self.__MONITOR.keys())
        else:
            parts = self.__MONITOR.keys()

        for part in parts:
            setattr(self, part, self.__MONITOR[part]())

    def os_usage(self, parts=None):
        if parts:
            self.check_parts(parts, Resource.all_os_usage_key())
        else:
            parts = Resource.all_os_usage_key()

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

    def proc_usage(self, pid=None, proc_name=None):
        proc_monitor = getattr(self, Resource.PROC.value, None)
        if not proc_monitor:
            setattr(self, Resource.PROC.value, self.__MONITOR[Resource.PROC.value])

        return proc_monitor.usage(pid=pid, proc_name=proc_name)
