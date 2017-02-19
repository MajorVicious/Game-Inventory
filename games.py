import click
import attr
import yaml
import os

FILENAME = 'inventory.yml'


@attr.s
class Game(object):
    name = attr.ib()
    min_player = attr.ib()
    max_player = attr.ib()
    genre = attr.ib()
    duration = attr.ib()


@click.command()
@click.option('--name', prompt='Game name')
@click.option(
    '--min-player', type=int, prompt='Min. number of players', default=2)
@click.option(
    '--max-player', type=int, prompt='Max. number of players', default=4)
@click.option('--genre', prompt='Game genre')
@click.option('--duration', type=int, prompt='Game duration (min)', default=5)
def add(*args, **kwargs):
    g = Game(*args, **kwargs)
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as f:
            inventory = yaml.load(f)
    else:
        inventory = []

    updated = False
    for existing in inventory:
        if existing['name'] == g.name:
            updated = True
            existing.update(g.__dict__)

    if not updated:
        inventory.append(g.__dict__)

    with open(FILENAME, 'w') as f:
        yaml.dump(inventory, f)

    if updated:
        print('{} updated'.format(g.name))
    else:
        print('{} added'.format(g.name))


def search():
    pass


def list():
    pass


if __name__ == '__main__':
    add()