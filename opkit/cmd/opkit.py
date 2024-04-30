import sys

import click

from opkit import __version__
from opkit.kit.kit import Kit
from opkit.common.constants import TODAY_DIR, NO_ARGS_MODES


echo = click.echo


@click.group(name='opkit',
             no_args_is_help=True,
             help='The entry point for all system operation and '
                  'maintenance work, which can access various sub '
                  'functions through sub commands',
             invoke_without_command=True)
@click.option('-v', '--version',
              is_flag=True,
              help="Get the opkit tool version number")
def opkit(version):
    """ 程序入口 """
    if not click.get_current_context().invoked_subcommand:
        if version:
            echo(__version__)
        else:
            echo(click.get_current_context().get_help())


@opkit.command(help='Monitor the resource usage and utilization rate of '
                    'the system or process, and if no parameters are passed '
                    'in, output the current operating system\'s resource '
                    'usage rate by default')
@click.option('-P', '--part',
              help="Default load monitor, multiple separated by commas")
@click.option('-p', '--pid',
              help='Output monitoring information for the specified process')
@click.option('-i', '--info',
              is_flag=True,
              help='Output process info, Need to be used '
                   'in conjunction with - p')
@click.option('-h', '--help',
              is_flag=True,
              help='Help info')
def monitor(part, pid, info, help):
    if help:
        echo(click.get_current_context().get_help())
        sys.exit(0)

    monitor_manager = Kit.load('monitor')
    wrap_func = monitor_manager.wrap_echo

    params = dict()
    if part:
        part_arr = part.split(',')
        params.update({'parts': part_arr})

    if pid:
        func = monitor_manager.proc_info \
            if info else monitor_manager.proc_usage
        params.update({'pid': pid})
    else:
        func = monitor_manager.os_usage

    res = func(**params)
    click.echo(wrap_func(res))


@opkit.command(help='Based on the original packet capture tool encapsulation, '
                    'add processes and namespaces as filtering criteria for '
                    'filtering')
@click.option('-c', '--count',
              default=0,
              help='Packet count, default 0')
@click.option('-w', '--worker',
              default=1,
              help='Specify worker thread, default 1')
@click.option('-f', '--filters',
              help='Packet filter rule')
@click.option('-i', '--iface',
              help='Network card')
@click.option('-p', '--pid',
              help='If the PID is set, packets will be captured from the port '
                   'that the specified process is listening to')
@click.option('-r', '--protocol',
              help='communication protocol')
@click.option('-s', '--sip',
              help='Filtering criteria, which will be converted to the src '
                   'host of the BPF filtering rule')
@click.option('-d', '--dip',
              help='Filtering criteria, which will be converted to the dst '
                   'host of the BPF filtering rule')
@click.option('-S', '--sport',
              help='Filtering criteria, which will be converted to the src '
                   'port of the BPF filtering rule')
@click.option('-D', '--dport',
              help='Filtering criteria, which will be converted to the dst '
                   'port of the BPF filtering rule')
@click.option('-n', '--namespace',
              help='Setting a network namespace will filter all process '
                   'packages under this namespace')
@click.option('-m', '--mark',
              default='and',
              help='Filter conditional connectors, and or or')
@click.option('-k', '--worker_params',
              help='Multi threading parameters')
@click.option('-t', '--timeout',
              default=30,
              help='Packet capture timeout exit time, default 30s')
@click.option('-o', '--out',
              help='The output method after capturing the package, '
                   'default output log, see kit.grab.handle for details')
@click.option('-I', '--include',
              help='Include column, separated by commas')
@click.option('-E', '--exclude',
              help='Exclude column, separated by commas')
@click.option('-h', '--help',
              is_flag=True,
              help='Help info')
def grab(count, worker, filters, iface, pid, protocol, sip, dip, sport, dport,
         namespace, mark, worker_params, timeout, out, include, exclude, help):
    if help:
        echo(click.get_current_context().get_help())
        sys.exit(0)

    params = {
        'count': count,
        'worker': worker,
        'filters': filters,
        'iface': iface,
        'pid': pid,
        'protocol': protocol,
        'sip': sip,
        'dip': dip,
        'sport': sport,
        'dport': dport,
        'namespace': namespace,
        'mark': mark,
        'worker_params': worker_params
    }

    grab_manager = Kit.load(
        'grab',
        **dict(init_workers=worker, timeout=timeout)
    )

    func = grab_manager.out_func.get(out)
    if func:
        params['prn'] = func

    res = grab_manager.grab(**params)
    include_arr = include.split(',') if include else None
    exclude_arr = exclude.split(',') if exclude else None

    echo(grab_manager.wrap_echo(res, include_arr, exclude_arr))
    echo("\n")
    echo("Capture data and output it to the {} directory".format(TODAY_DIR))


@opkit.command(
    no_args_is_help=True,
    help='Process tracking command, which allows opkit tools to '
         'easily manipulate the memory of Python processes. the '
         'currently supported modes are r(read) wv(write_val) '
         'da(dict_add) dd(dict_del) la(list_append) lr(list_remove)'
         'os(object_set) mv(mem_view) ri(rpdb_inject) x(exec_script)'
)
@click.argument('pid', required=True)
@click.argument('mode', required=True, default='r')
@click.argument('args', nargs=-1, required=False, metavar='ARG [ARG2 ...]')  # noqa
@click.option('-h', '--help',
              is_flag=True,
              help='Help info')
def trace(pid, mode, args, help):
    if help:
        echo(click.get_current_context().get_help())
        sys.exit(0)

    if not pid:
        echo("Please enter PID")
        sys.exit(1)

    if not args and mode not in NO_ARGS_MODES:
        echo("Please enter kwargs")
        sys.exit(1)

    trace_manager = Kit.load(
        'trace',
        **dict(pid=pid)
    )

    def parse_args(_args):
        arg_vals = []
        for arg in _args:
            parts = arg.split(":")

            val_str = parts[0].strip()
            if len(parts) < 2:
                type_str = ''
            else:
                type_str = parts[1].strip()

            if type_str == 'int':
                val = int(val_str)
            elif type_str == 'float':
                val = float(val_str)
            elif type_str == 'bool':
                val = bool(val_str)
            elif type_str == 'str':
                val = val_str
            else:
                try:
                    val = eval(val_str)
                except Exception:
                    val = val_str

            arg_vals.append(val)

        return arg_vals

    args = parse_args(args) if mode != 'x' else args
    res = trace_manager.do(mode, *args)

    echo(res)


def hack():
    pass
