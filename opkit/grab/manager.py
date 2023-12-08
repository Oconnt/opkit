from concurrent import futures
from scapy.sendrecv import sniff

from opkit.common.constants import MAX_WORKER
from opkit.grab import handle


class Manager(object):
    """ 抓包管理 """

    def __init__(self, init_workers=1, timeout=30):
        self.pool = futures.ThreadPoolExecutor(max_workers=min(init_workers, MAX_WORKER))
        self.timeout = timeout

    def _grab(self,
              prn=handle.record,
              count=0,
              timeout=None,
              iface=None,
              protool=None,
              sip=None,
              dip=None,
              sport=None,
              dport=None,
              ):
        sniff_params = {
            "prn": prn,
            "count": count,
            "timeout": timeout,
            "iface": iface
        }

        query = {
            'protool': protool,
            'sip': sip,
            'dip': dip,
            'sport': sport,
            'dport': dport
        }
        filters = self._generate_filters(**query)

        if filters:
            sniff_params.update(filter=filters)

        pkg = sniff(**sniff_params)
        return pkg

    @staticmethod
    def _generate_filters(protool=None,
                          sip=None,
                          dip=None,
                          sport=None,
                          dport=None,
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
            filters.append(f"src port {sport}")

        # 添加目的端口过滤条件
        if dport:
            filters.append(f"dst port {dport}")

        # 组合所有过滤条件
        bpf_filter = ""
        if filters:
            bpf_filter = " and ".join(filters)

        return bpf_filter

    def grab(self, worker=1, **kwargs):
        with self.pool as execute:
            fs = []
            for _ in range(worker):
                future = execute.submit(self._grab, **kwargs)
                fs.append(future)

            for f in futures.as_completed(fs):
                try:
                    res = f.result(self.timeout)
                    print("pkg: {}".format(res))
                except Exception as e:
                    print("Error occurred: {}".format(e))

