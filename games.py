import click
import attr
import yaml
import os
import prettytable
import random
import datetime



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
    '--level', type=str, prompt='Difficulty(Novice, Intermediate, Expert)', 
    default='Intermediate')
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
        played(results)


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
        table.add_row([game[field] for field in fields])
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

def update(game):
    filename = define_list()

    with open(filename, 'r') as f:
        inventory = yaml.load(f)

    for existing in inventory:
        if existing["name"] == game["name"]:
            existing["last_played"] = game["last_played"]
            existing["stars"] = game["stars"]


    with open(filename, 'w') as f:
        yaml.dump(inventory, f)


@cli.command()
@click.option('--data', prompt="Do you want to use the default list ?")
def newList(data):
    if data.lower() == 'y' or data == '':
        filename = define_list()
    elif data.lower() == 'n':
        filename = input("Enter the name of your game list, with the extension '.yml'")


    with open('properties.txt', 'w') as p:
        save = {"Default list": filename}
        yaml.dump(save, p)

def played(results):
    temp = []
    for result in results:
        play = input("Do you played the game ? ")
        if play.lower() == "y":
            temp.append(result)
            for game in temp:
                day = datetime.date.today()
                game["last_played"] = datetime.date.strftime(day, '%d-%m-%Y')
                star = starred(game)
                update(star)
        else:
            pass

def starred(game):
    star = input("Do you want to rate the game ? ")
    if star.lower() == "y":
        rate = eval(input("How many star ? from 0 to 5 "))
        game["stars"] = rate
        return game
    else:
        pass

#Configuration file

def define_list():
    with open('properties.txt', 'r') as p:
        list_used = yaml.load(p)
        filename = list_used["Default list"]
    return filename



if __name__ == '__main__':
    cli()