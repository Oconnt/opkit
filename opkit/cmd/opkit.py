import click

from opkit import __version__
from opkit.kit.kit import Kit


echo = click.echo


@click.group(name='opkit',
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
def monitor(part, pid, info):
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
@click.option('-I', '--include',
              help='Include column, separated by commas')
@click.option('-E', '--exclude',
              help='Exclude column, separated by commas')
def grab(count, worker, filters, iface, pid, protocol, sip, dip, sport, dport,
         namespace, mark, worker_params, timeout, include, exclude):
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

    res = grab_manager.grab(**params)
    include_arr = include.split(',') if include else None
    exclude_arr = exclude.split(',') if exclude else None

    echo(grab_manager.wrap_echo(res, include_arr, exclude_arr))


def hack():
    pass
