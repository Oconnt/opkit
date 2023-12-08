import click


@click.Command(name="opkit",
               help="The entry point for all system operation and maintenance work, "
                    "which can access various sub functions through sub commands")
@click.group(name="opkit")
@click.option('-v', '--version',
              help="Get the opkit tool version number")
def opkit():
    """"""