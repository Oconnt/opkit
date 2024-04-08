import socket
from enum import Enum

# 根路径
ROOT_PATH = "/"
# 本机ip
LOCALHOST = "127.0.0.1"
# 最大线程数
MAX_WORKER = 10

# =================================== grab ====================================
# 默认garb日志文件
DEFAULT_GRAB_LOG_FILE = "/var/log/opkit/today/grab.log"
# 默认pcap文件
DEFAULT_PCAP_FILE = "/var/log/opkit/today/grab.pcap"

# ================================== logging ==================================
# 默认文件目录
DEFAULT_LOG_DIR = "/var/log/opkit"
# today目录
TODAY_DIR = "/var/log/opkit/today"
# 默认输出log文件
DEFAULT_LOG_FILE = "/var/log/opkit/today/opkit.log"
# 写入模式
DEFAULT_MODE = "a+"
# 编码
DEFAULT_ENCODING = "utf-8"
# 日志格式
DEFAULT_FORMAT = "%(asctime)s %(name)s %(thread)d %(levelname)s %(message)s"

# =================================== socket ==================================
PREFIX = "IPPROTO_"
proto_table = {num: name[len(PREFIX):] for name, num in vars(socket).items()
               if name.startswith(PREFIX)}

# ==================================== PEM ====================================
PEM_START_FLAG = "BEGIN CERTIFICATE"

# =================================== trace ===================================
DEFAULT_START_ADDR = 0
DEFAULT_END_ADDR = 0xFFFFFFFFFFFFFFFF


class ValueEnum(Enum):

    @classmethod
    def values(cls):
        return list(cls.__members__.values())


class Resource(ValueEnum):

    CPU = "cpu"
    MEM = "memory"
    DISK = "disk"
    NET = "network"
    PROC = "process"

    @classmethod
    def all_os_usage_key(cls):
        return [cls.CPU.value, cls.MEM.value, cls.DISK.value]

    @classmethod
    def all_proc_usage_key(cls):
        return [cls.CPU.value, cls.MEM.value]

    @staticmethod
    def wrap(resource, unit=None):
        if unit and isinstance(unit, Unit):
            return "".join([resource, '(', unit.value, ')'])

        return resource


class Unit(ValueEnum):

    PERCENT = "%"


class CPUMetrics(ValueEnum):

    USAGE_RATE = "usage_rate"
    COUNT = "count"
    HZ = "hz"


class MemoryMetrics(ValueEnum):

    USAGE_RATE = "usage_rate"
    FREE = "free"
    USED = "used"
    TOTAL = "total"


class DiskMetrics(ValueEnum):

    USAGE_RATE = "usage_rate"
    FREE = "free"
    USED = "used"
    TOTAL = "total"


class NetworkMetrics(ValueEnum):

    CONN_COUNT = "conn_count"


class GrabOutFunc(ValueEnum):

    LOG = 'log'
    PCAP = 'pcap'


class TraceFlag(ValueEnum):

    LIST = ['l', 'list']
    WRITE = ['w', 'write']
