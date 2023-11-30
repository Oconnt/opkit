from enum import Enum


ROOT_PATH = "/"


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
    def all_usage_key(cls):
        return [cls.CPU.value, cls.MEM.value, cls.DISK.value]


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