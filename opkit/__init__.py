from opkit.monitor.manager import Manager
from opkit.utils.print_util import print_dict

if __name__ == '__main__':
    m = Manager()
    print_dict(m.usage())
