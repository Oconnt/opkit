from opkit.kit.monitor.manager import Manager as MonitorManager
from opkit.kit.grab.manager import Manager as GrabManager
from opkit.kit.hack.manager import Manager as HackManager
from opkit.kit.trace.manager import Manager as TraceManager

from opkit.utils.common_util import get_method_params


class Kit(object):

    __abi__ = {
        'monitor': MonitorManager,
        'grab': GrabManager,
        'hack': HackManager,
        'trace': TraceManager
    }

    def __str__(self):
        res = "({})"
        fmt = []
        for abi in self.__abi__:
            fmt.append("=".join([abi, str(getattr(self, abi, 'None'))]))

        fmt_str = ", ".join(fmt)
        return res.format(fmt_str)

    @classmethod
    def load(cls, abi, **params):
        cls.check_init_abi(abi)

        clz = cls.__abi__[abi]
        prs = get_method_params(clz, '__init__')
        prs_dict = {name: value
                    for name, value in params.items() if name in prs}

        return clz(**prs_dict)

    @classmethod
    def check_init_abi(cls, *abi):
        for key in abi:
            if key not in cls.__abi__:
                raise ValueError("unknown abi %s" % key)
