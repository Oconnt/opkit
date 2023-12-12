import time
from scapy.utils import wrpcap

from opkit.common.constants import DEFAULT_PCAP_FILE
from opkit.common.log import get_today_dir
from opkit.utils.os_util import create_file


def pcap(pcap_file=DEFAULT_PCAP_FILE, new=False):
    """ 输出pcap文件 """

    def handler(pkg):
        if new:
            timestamp = str(int(time.time()))
            f = '/'.join([get_today_dir(), 'grab_%s.pcap' % timestamp])
        else:
            f = pcap_file

        try:
            create_file(f)
            wrpcap(f, pkg)
        except ValueError as e:
            print("create to pcap file fail, err: {}".format(e))
            raise
        except Exception as e:
            print("output pcap file fail, err: {}".format(e))
            raise

    return handler
