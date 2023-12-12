import tabulate
from prettytable import PrettyTable


def print_dict(data):
    if not isinstance(data, dict):
        return

    table = PrettyTable()
    table.field_names = list(data.keys())
    table.add_row(list(data.values()))

    print(table)


def print_dict_list(ls):
    if (not ls or not isinstance(ls, list) or
            not all([isinstance(it, dict) for it in ls])):
        return

    res = find_all_data(ls)
    table = tabulate.tabulate(res, headers='keys')

    print(table)


def find_all_data(arr):
    res = dict()

    def find_dict_data(d):
        for val in d.values():
            if isinstance(val, dict):
                return find_dict_data(val)

        return d

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
