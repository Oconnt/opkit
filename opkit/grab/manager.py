from concurrent import futures

import psutil
from scapy.sendrecv import sniff

from opkit.common.constants import MAX_WORKER
from opkit.utils.print_util import print_dict_list
from opkit.utils.os_util import get_netns_pids
from opkit.grab import handle


class Manager(object):
    """ 抓包管理 """

    def __init__(self, init_workers=1, timeout=30):
        self.pool = futures.ThreadPoolExecutor(max_workers=min(init_workers, MAX_WORKER))
        self.timeout = timeout

    def _grab(self,
              prn=handle.output_log,
              count=0,
              timeout=None,
              pid=None,
              namespace=None,
              iface=None,
              protool=None,
              sip=None,
              dip=None,
              sport=None,
              dport=None,
              pre_kw=None
              ):
        if not pre_kw:
            pre_kw = {}

        sniff_params = {
            "prn": prn(**pre_kw),
            "count": count,
            "timeout": timeout,
            "iface": iface
        }

        query = {
            'pid': pid,
            'namespace': namespace,
            'protool': protool,
            'sip': sip,
            'dip': dip,
            'sport': sport,
            'dport': dport
        }
        filters = self._generate_filters(**query)

        if filters:
            sniff_params.update(filter=filters)

        pkgs = sniff(**sniff_params)
        return self._handle_pkg(pkgs)

    def _generate_filters(self,
                          protool=None,
                          sip=None,
                          dip=None,
                          sport=None,
                          dport=None,
                          pid=None,
                          namespace=None
                          ):
        filters = []
        # 添加协议过滤条件
        if protool:
            filters.append(protool)

        # 添加源IP地址过滤条件
        if sip:
            filters.append("src host {}".format(sip))

        # 添加目的IP地址过滤条件
        if dip:
            filters.append("dst host {}".format(dip))

        # 添加源端口过滤条件
        if sport:
            filters.append("src port {}".format(sport))

        # 添加目的端口过滤条件
        if dport:
            filters.append("dst port {}".format(dport))

        # 添加pid过滤条件
        if pid:
            ports = self.get_process_ports(pid)
            for port in ports:
                filters.append("port {}".format(port))

        # 添加namespace过滤条件
        if namespace:
            ports = self.get_netns_ports(namespace)
            for port in ports:
                filters.append("port {}".format(port))

        # 组合所有过滤条件
        bpf_filter = ""
        if filters:
            bpf_filter = " and ".join(filters)

        return bpf_filter

    def grab(self, worker=1, include=None, exclude=None, **kwargs):
        print("start grab packet, worker thread count: ", worker)
        with self.pool as execute:
            fs = []
            for _ in range(worker):
                future = execute.submit(self._grab, **kwargs)
                fs.append(future)

            for f in futures.as_completed(fs):
                try:
                    res = f.result(self.timeout)
                    print_dict_list(res, include=include, exclude=exclude)
                except Exception as e:
                    print("Error occurred: {}".format(e))
                    raise

        print("grab packet done")

    def _handle_pkg(self, pkgs):
        return [handle.analysis(pkg) for pkg in pkgs]

    def get_process_ports(self, pid):
        connections = psutil.Process(pid).connections()
        ports = []
        for conn in connections:
            if conn.status == 'LISTEN':
                laddr = conn.laddr
                ports.append(laddr.port)

        return ports

    def get_netns_ports(self, namespace):
        pids = get_netns_pids(namespace)
        ports = []
        for pid in pids:
            ports.extend(self.get_process_ports(pid))

        return ports
