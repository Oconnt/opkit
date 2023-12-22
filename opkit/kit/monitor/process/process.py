import psutil

from collections import OrderedDict
from datetime import datetime

from opkit.kit.monitor.base import (
    BaseMonitor,
)
from opkit.common.constants import (
    Resource,
    Unit
)


class ProcessMonitor(BaseMonitor):

    MONITOR_NAME = "process"

    def usage(self, pid=None, proc_name=None, parts=None):
        """
        获取进程使用率
        :param proc_name:
        :param pid:
        :param parts:
        :return:
        """
        return self.info(
            pid,
            proc_name,
            ["cpu", "memory"] if not parts else parts
        )

    def info(self, pid=None, proc_name=None, parts=None):
        """
        获取进程信息
        :param pid: 进程id
        :param proc_name: 进程名
        :param parts: 返回属性集
        :return:
        """
        res = OrderedDict()

        if not pid:
            if not isinstance(proc_name, str):
                raise TypeError("process name must be str, type: %s", type(proc_name))  # noqa

            name = proc_name.lower()
            pid = self._find_pid(name)
            if not pid:
                return res

        pid = int(pid)
        p = psutil.Process(pid)

        res["pid"] = p.pid
        res["name"] = p.name()
        res["create_time"] = datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S")  # noqa
        res["running_time"] = datetime.now() - datetime.fromtimestamp(p.create_time())  # noqa
        res["status"] = p.status()
        res[Resource.CPU.value] = "{:.2f}".format(p.cpu_percent())
        res[Resource.MEM.value] = "{:.2f}".format(p.memory_percent())
        res["tcp_count"] = len(p.connections("tcp"))
        res["udp_count"] = len(p.connections("udp"))

        if parts:
            res = self._filter_attrs(res, parts)

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

        attrs = sorted(attrs, key=attrs.index)
        fir_res = OrderedDict()
        for attr in attrs:
            if not isinstance(attr, str):
                continue

            fir_res[attr] = res.get(attr)

        return fir_res
