import os

from scapy.layers.l2 import Ether

from opkit.common.constants import DEFAULT_RECORD_FILE
from opkit.utils.os_util import is_exist


def _analysis(packet):
    packet_dict = {}

    # 解析源地址、目标地址、协议类型和数据长度
    packet_dict["source"] = packet[Ether].src
    packet_dict["destination"] = packet[Ether].dst
    packet_dict["protocol"] = packet[Ether].name
    packet_dict["length"] = len(packet)

    # 解析数据内容
    if packet.haslayer("Raw"):
        packet_dict["data"] = packet.getlayer("Raw").load.decode('utf-8')
    else:
        packet_dict["data"] = None

    # 处理完毕后返回字典
    return packet_dict


def record(pkg, record_file=DEFAULT_RECORD_FILE):
    if not is_exist(record_file):
        dir_path = os.path.dirname(record_file)
        os.makedirs(dir_path, exist_ok=True)

        open(record_file, "w")
        os.chmod(record_file, 0o666)

    result = _analysis(pkg)

    print("result: {}".format(result))
