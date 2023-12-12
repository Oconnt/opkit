from opkit.grab.manager import Manager as Grab
from opkit.monitor.manager import Manager as Monitor
from opkit.utils.print_util import print_dict, print_dict_list


if __name__ == '__main__':
    # m = Monitor()
    # print_dict(m.proc_usage(20768))
    # print_dict(m.process.info(19184, attrs=["name", "tcp_count", "udp_count"]))

    g = Grab()
    g.grab(count=3)
    # bt = b'\x06\xde$\xcb\xc5\xed7\x82\xba\x01-H\x0e2\xb6\x86\xc15\x90h\x04t\xc4\xbf\xcd\x84\xaceu\xb6\xb7Vu\xda\x1e\xc1p\xb9M\x19#\xbc@\xc5\xe2\xf1\xf7\x08\x8b\xfeZ\xd6I\x88\xafU\\UH:\xd1\xdbY\xf0T\xc0\xf6\xef\x8b3\xd6f\x01\xd8\x02\xfe)\x8c#\xc8'
    # print(chardet.detect(bt))
    # print(bt.decode("windows-1253"))
