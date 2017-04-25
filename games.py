import click
import attr
import yaml
import os
import prettytable
import random
import datetime as dt


DATE_FORMAT = '%d-%m-%Y'

GAME_DIFFICULTY = {1 : "Novice",
                   2 : "Intermediate",
                   3 : "Expert"}


@attr.s
class Game(object):
    name = attr.ib()
    min_player = attr.ib()
    max_player = attr.ib()
    genre = attr.ib()
    duration = attr.ib()
    level = attr.ib()
    last_played = attr.ib(default=None)
    stars = attr.ib(default=None)



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
@click.option(
    '--level', type=int, prompt=("Difficulty({}),").format(",".join(map(str, GAME_DIFFICULTY.keys()))),
    default=2)
def add(*args, **kwargs):
    g = Game(*args, **kwargs)
    save(g)

@cli.command()
@click.option('--player', prompt="How many players ?", default=2)
@click.option('--time', prompt="How many time have you ?", default=60)
def search(player, time):
    candidates = []
    inventory = load()
    for game in inventory:
        if (game["min_player"] <= player <= game["max_player"]
                and game["duration"] <= time):
            candidates.append(game)

    if candidates:
        results = []
        while sum(item["duration"] for item in results) < time and candidates:
            choice = random.choice(candidates)
            if sum(item["duration"] for item in results) + choice["duration"] > time:
                break

            results.append(choice)
            candidates.remove(choice)

        show(results)


    else:
        print("There is no game to choose from.")

def load():
    filename = define_list()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            inventory = yaml.load(f)
            return inventory
    else:
        raise Exception("No inventory file found")

def show(inventory):
    fields = [x.name for x in Game.__attrs_attrs__]
    table = prettytable.PrettyTable()
    table.field_names = fields
    for game in inventory:
        temp = []
        for field in fields:
            if field == "level":
                temp.append(GAME_DIFFICULTY[game[field]])
            else:
                temp.append(game[field])

        table.add_row(temp)
    print(table)


@cli.command()
@click.option('--sort', prompt='Field to sort with', default='name')
def list(sort):
    inventory = load()
    inventory.sort(key=lambda x: x[sort])
    show(inventory)

def save(game):
    filename = define_list()

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            inventory = yaml.load(f)
    else:
        inventory = []

    updated = False
    for existing in inventory:
        if existing['name'] == game.name:
            updated = True
            existing.update(game.__dict__)

    if not updated:
        inventory.append(game.__dict__)

    with open(filename, 'w') as f:
        yaml.dump(inventory, f)

    if updated:
        print('{} updated'.format(game.name))
    else:
        print('{} added'.format(game.name))

#Rating and Timestamp

@cli.command()
@click.option('--name', prompt="Choose a game for the timestamp")
def time_stamp(name):
    inventory = load()
    for game in inventory:
        if game["name"] == name:
            game["last_played"] = dt.date.strftime(dt.date.today(), DATE_FORMAT)
            update(game)

@cli.command()
@click.option('--name', prompt='Choose a game to rate')
@click.option('--rate', prompt="Rate the game")
def rate(name, rate):
    inventory = load()
    for game in inventory:
        if game['name'] == name:
            game["stars"] = rate
            update(game)

def update(game):
    inventory = load()
    filename = define_list()
    for game_to_update in inventory:
        if game_to_update["name"] == game["name"]:
            game_to_update["last_played"] = game["last_played"]
            game_to_update["stars"] = game["stars"]

    with open(filename, 'w') as f:
        yaml.dump(inventory, f)

#Configuration file

@cli.command()
@click.option('--data', prompt="Do you want to use the default list ?")
def newList(data):
    if data.lower() == 'y' or data == '':
        filename = define_list()
    elif data.lower() == 'n':
        filename = input("Enter the name of your game list, with the extension '.yml' ")


    with open('properties.txt', 'w') as p:
        default_list = {"default_list": filename}
        yaml.dump(default_list, p)

def define_list():
    with open('properties.txt', 'r') as p:
        list_used = yaml.load(p)
        filename = list_used["default_list"]
    return filename

@cli.command()
def update_list():
    filename = define_list()
    inventory = load()
    fields = [x.name for x in Game.__attrs_attrs__]
    for game in inventory:
        for field in fields:
            if field not in game.keys():
                if field == "level":
                    game[field] = 2
                else:
                    game[field] = None

    
    with open(filename, 'w') as f:
        yaml.dump(inventory, f)


if __name__ == '__main__':
    cli()
