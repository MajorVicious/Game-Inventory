import click

@click.group()
def cli():
    pass

@cli.command()
@click.option('--item', type=(str, int))
def putitem(item):
    click.echo('name=%s id=%d' % item)


if __name__ == '__main__':
    cli()
