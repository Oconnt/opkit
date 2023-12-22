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


@opkit.command(help='monitor the resource usage and utilization rate of '
                    'the system or process, and if no parameters are passed '
                    'in, output the current operating system\'s resource '
                    'usage rate by default')
@click.option('-P', '--part',
              help="default load monitor, multiple separated by commas")
@click.option('-p', '--pid',
              help='output monitoring information for the specified process')
@click.option('-i', '--info',
              is_flag=True,
              help='output process info, Need to be used '
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


@opkit.command(help='based on the original packet capture tool encapsulation, '
                    'add processes and namespaces as filtering criteria for '
                    'filtering')
@click.option('-c', '--count',
              default=0,
              help='packet count, default 0')
@click.option('-w', '--worker',
              default=1,
              help='specify worker thread, default 1')
@click.option('-i', '--iface',
              help='network card')
@click.option('-p', '--pid',
              help='process id')
@click.option('-r', '--protocol',
              help='communication protocol')
@click.option('-s', '--sip',
              help='src ip')
@click.option('-d', '--dip',
              help='dst ip')
@click.option('-S', '--sport',
              help='src port')
@click.option('-D', '--dport',
              help='dst port')
@click.option('-n', '--namespace',
              help='network namespace')
@click.option('-k', '--worker_params',
              help='multi threading parameters')
@click.option('-t', '--timeout',
              default=30,
              help='packet capture timeout exit time, default 30s')
@click.option('-I', '--include',
              help='include column, separated by commas')
@click.option('-E', '--exclude',
              help='exclude column, separated by commas')
def grab(count, worker, iface, pid, protocol, sip, dip, sport, dport,
         namespace, worker_params, timeout, include, exclude):
    params = {
        'count': count,
        'worker': worker,
        'iface': iface,
        'pid': pid,
        'protocol': protocol,
        'sip': sip,
        'dip': dip,
        'sport': sport,
        'dport': dport,
        'namespace': namespace,
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
