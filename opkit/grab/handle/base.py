from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import Ether

from opkit.common.constants import proto_table


def analysis(packet, decode="utf-8"):
    packet_dict = {}

    if packet.haslayer("Ethernet"):
        eth = packet_dict["Ethernet"] = {}
        eth["src_mac"] = packet[Ether].src
        eth["dst_mac"] = packet[Ether].dst

    if packet.haslayer("IP"):
        ip = packet_dict["IP"] = {}
        ip["protocol"] = proto_table[packet[IP].proto]
        ip["src_ip"] = packet[IP].src
        ip["dst_ip"] = packet[IP].dst
        ip["ttl"] = packet[IP].ttl

    if packet.haslayer("TCP"):
        tcp = packet_dict["TCP"] = {}
        tcp["src_port"] = packet[TCP].sport
        tcp["dst_port"] = packet[TCP].dport

    if packet.haslayer("UDP"):
        udp = packet_dict["UDP"] = {}
        udp["src_port"] = packet[UDP].sport
        udp["dst_port"] = packet[UDP].dport

    # 解析数据内容
    if packet.haslayer("Raw"):
        packet_dict["data"] = _decode_raw(packet.getlayer("Raw"), decode)

    # 处理完毕后返回字典
    return packet_dict


def _decode_raw(raw, decode="utf-8"):
    load = raw.load

    try:
        return load.decode(decode)
    except Exception as e:
        print("decode raw fail, err: {}".format(e))
        return load
