import psutil

from collections import OrderedDict
from datetime import datetime

from opkit.monitor.base import (
    BaseMonitor,
    Check
)
from opkit.common.constants import (
    Resource,
    Unit
)


class ProcessMonitor(BaseMonitor, Check):

    MONITOR_NAME = "process"

    def usage(self, pid=None, proc_name=None, parts=None):
        """
        获取进程使用率
        :param proc_name:
        :param pid:
        :param parts:
        :return:
        """
        if parts:
            self.check_parts(parts, Resource.all_proc_usage_key())
        else:
            parts = Resource.all_proc_usage_key()

        res = OrderedDict()
        if not pid:
            pid = self._find_pid(proc_name)
            if not pid:
                return res

        p = psutil.Process(pid)
        unit = Unit.PERCENT

        for part in parts:
            res[Resource.wrap(part, unit)] = p.cpu_percent()

        return res

    def info(self, pid=None, proc_name=None, attrs=None):
        """
        获取进程信息
        :param pid: 进程id
        :param proc_name: 进程名
        :param attrs: 返回属性集
        :return:
        """
        res = OrderedDict()

        if not pid:
            pid = self._find_pid(proc_name)
            if not pid:
                return res

        p = psutil.Process(pid)
        percent = Unit.PERCENT

        res["pid"] = p.pid
        res["name"] = p.name()
        res["create_time"] = datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S")
        res["running_time"] = datetime.now() - datetime.fromtimestamp(p.create_time())
        res["status"] = p.status()
        res[Resource.wrap(Resource.CPU.value, percent)] = "{:.2f}".format(p.cpu_percent())
        res[Resource.wrap(Resource.MEM.value, percent)] = "{:.2f}".format(p.memory_percent())
        res["tcp_count"] = len(p.connections("tcp"))
        res["udp_count"] = len(p.connections("udp"))

        if attrs:
            res = self._filter_attrs(res, attrs)

        return res

    @staticmethod
    def _find_pid(proc_name):
        pid = None
        for p in psutil.process_iter(['pid', 'name']):
            if p.name() == proc_name:
                pid = p.pid
                break

        return pid

    @staticmethod
    def _filter_attrs(res, attrs):
        iter_types = (list, set, tuple, frozenset)
        if not isinstance(attrs, iter_types):
            raise TypeError("invalid attrs type %s" % type(attrs))

        attrs = set(attrs)
        fir_res = OrderedDict()
        for attr in attrs:
            if not isinstance(attr, str):
                continue

            fir_res[attr] = res.get(attr)

        return fir_res
