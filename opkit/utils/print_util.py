from prettytable import PrettyTable


def print_dict(data):
    if not isinstance(data, dict):
        return

    table = PrettyTable()
    table.field_names = list(data.keys())
    table.add_row(list(data.values()))

    print(table)
