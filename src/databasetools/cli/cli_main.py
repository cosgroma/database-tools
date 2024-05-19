import click

# from .commands.program_commands import program_commands
# from .commands.scan_commands import scan_commands

# pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
# @pass_context
def cli():
    ...
    # Config.load()


@click.command(name="help")
def help_command():
    """Print help message."""
    click.echo("SERGEANT CLI")


cli.add_command(help_command)
# cli.add_command(scan_commands)

if __name__ == "__main__":
    cli()
