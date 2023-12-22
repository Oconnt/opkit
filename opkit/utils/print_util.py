from collections import OrderedDict
from prettytable import PrettyTable


def print_dict(data, include=None, exclude=None):
    if not isinstance(data, dict):
        return

    print_dict_list([data], include, exclude)


def print_dict_list(ls, include=None, exclude=None):
    if (not ls or not isinstance(ls, list) or
            not all([isinstance(it, dict) for it in ls])):
        return

    def __include(data, in_key):
        cp_data = data.copy()
        for key in cp_data:
            if key not in in_key:
                data.pop(key)

        return data

    def __exclude(data, ex_key):
        cp_data = data.copy()
        for key in cp_data:
            if key in ex_key:
                data.pop(key)

        return data

    res = find_all_data(ls)
    if include:
        res = __include(res, include)
    elif exclude:
        res = __exclude(res, exclude)

    table = PrettyTable()
    lens = [len(vals) for vals in res.values()]
    col_len = max(*lens)
    for field, vals in res.items():
        cot = len(vals)
        if cot < col_len:
            vals.extend((col_len - cot) * [""])

        table.add_column(field, vals)

    print(table)


def find_all_data(arr):
    res = OrderedDict()

    for d in arr:
        for k, v in d.items():
            if isinstance(v, dict):
                date_d = find_dict_data(v)
                for key, val in date_d.items():
                    arr = res.get(key, [])
                    arr.append(val)
                    res[key] = arr
            else:
                arr = res.get(k, [])
                arr.append(v)
                res[k] = arr

    return res


def find_dict_data(d):
    for val in d.values():
        if isinstance(val, dict):
            return find_dict_data(val)

    return d
