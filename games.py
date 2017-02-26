import click
import attr
import yaml
import os
import prettytable
import random

FILENAME = 'inventory.yml'


@attr.s
class Game(object):
    name = attr.ib()
    min_player = attr.ib()
    max_player = attr.ib()
    genre = attr.ib()
    duration = attr.ib()


@click.group()
def cli():
    pass


@cli.command()
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

@cli.command()
@click.option('--player', prompt="How many players ?", default=2)
@click.option('--time', prompt="How many time have you ?", default=60)
def search(player, time):
    candidates = []
    inventory = load()

    for game in inventory:
        if game["min_player"] <= player <= game["max_player"] and game["duration"] <= time:
            candidates.append(game)


    if candidates:
        results = []
        while sum(item["duration"] for item in results) < time:
            choice = random.choice(candidates)
            if sum(item["duration"] for item in results) + choice["duration"] > time:
                break

            results.append(choice)
            candidates.remove(choice)

        show(results)


    else:
        print("There is no game to choose from.")

def load():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as f:
            inventory = yaml.load(f)
            return inventory
    else:
        raise Exception("No inventory file found")

def show(inventory):
    fields = [x.name for x in Game.__attrs_attrs__]
    table = prettytable.PrettyTable()
    table.field_names = fields
    for game in inventory:
        table.add_row([game[field] for field in fields])
    print(table)


@cli.command()
@click.option('--sort', prompt='Field to sort with', default='name')
def list(sort):
    inventory = load()
    inventory.sort(key=lambda x: x[sort])
    show(inventory)


if __name__ == '__main__':
    cli()
