from opkit.utils.print_util import print_dict, print_dict_list


class BaseManager(object):

    @staticmethod
    def wrap_echo(data, include=None, exclude=None):
        if isinstance(data, dict):
            print_dict(data)
        elif isinstance(data, list) and all([isinstance(d, dict) for d in data]):  # noqa
            print_dict_list(data, include, exclude)
        else:
            print(data)
