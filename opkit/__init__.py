from opkit.grab.manager import Manager as Grab
from opkit.monitor.manager import Manager as Monitor
from opkit.utils.print_util import print_dict, print_dict_list


if __name__ == '__main__':
    # m = Monitor()
    # print_dict(m.proc_usage(20768))
    # print_dict(m.process.info(19184, attrs=["name", "tcp_count", "udp_count"]))

    g = Grab()
    g.grab(count=1, include=["src_mac", "dst_mac"], exclude=['data'])
