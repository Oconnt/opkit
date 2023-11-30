import psutil

from opkit.monitor.base import BaseMonitor
from opkit.common.constants import ROOT_PATH


class CPUMonitor(BaseMonitor):

    MONITOR_NAME = "cpu"

    @staticmethod
    def usage(interval=None, percpu=False):
        """ 返回系统cpu使用率 """
        res = psutil.cpu_percent(interval, percpu)
        return res

    @staticmethod
    def count(logic=True):
        """
        返回系统cpu个数
        :param logic: 是否返回仅返回物理cpu核数
        :return:
        """
        return psutil.cpu_count(logic)


class MemoryMonitor(BaseMonitor):

    MONITOR_NAME = "memory"

    def usage(self):
        """ 返回内存使用率 """
        return self._vir_mem().percent

    def used(self):
        """ 返回内存使用量 """
        return self._vir_mem().used

    def total(self):
        """ 返回内存使用总量 """
        return self._vir_mem().total

    def free(self):
        """ 返回内存可用总量 """
        return self._vir_mem().free

    @staticmethod
    def _vir_mem():
        return psutil.virtual_memory()

    @staticmethod
    def _swap_mem():
        return psutil.swap_memory()


class DiskMonitor(BaseMonitor):

    MONITOR_NAME = "disk"

    def usage(self, path=ROOT_PATH):
        return self._disk(path).percent

    @staticmethod
    def _disk(path=ROOT_PATH):
        return psutil.disk_usage(path)


class NetworkMonitor(BaseMonitor):

    MONITOR_NAME = "network"

    @staticmethod
    def conn_count(kind):
        return len(psutil.net_connections(kind))
