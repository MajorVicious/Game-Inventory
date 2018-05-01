import math
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
import datetime
import yaml
import os
import random

app = Flask(__name__)
app.config['INVENTORY_FILE'] = os.path.abspath(
    os.path.join(os.path.dirname(os.getcwd()), "inventory.yml"))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'CHANGEME'
db = SQLAlchemy(app)
admin = Admin(app, name='games', template_mode='bootstrap3', url='/')
manager = Manager(app)

user_library = db.Table(
    'user_library', db.metadata,
    db.Column('library_id', db.Integer, db.ForeignKey("library.id")),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))

game_library = db.Table(
    'game_library', db.metadata,
    db.Column('library_id', db.Integer, db.ForeignKey("library.id")),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id')))


class ExportableModelView(ModelView):
    can_export = True


class LibraryModelView(ModelView):
    column_list = ('name', 'games', 'users')


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    skill = db.Column(db.Integer)

    def __init__(self, name, skill):
        self.name = name
        self.skill = skill

    def __str__(self):
        return self.name


class Stars(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, unique=True)

    def __init__(self, amount):
        self.amount = amount

    def __str__(self):
        return '*' * self.amount


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), unique=True, nullable=False)
    min_player = db.Column(db.Integer, default=2)
    max_player = db.Column(db.Integer, default=4)
    duration = db.Column(db.Integer, default=60)

    last_played = db.Column(db.Date, default=None)

    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))
    genre = db.relationship(Genre)

    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    level = db.relationship(Level)

    def features(self):
        return {
            'name': self.name,
            'genre': self.genre_id,
            'level': self.level_id,
            # 'min_player': self.min_player,
            # 'max_player': self.max_player,
            'players': ((self.max_player + self.min_player) / 2),
            'duration': self.duration
        }

    def __sub__(self, other):
        a = self.features().copy()
        b = other.features().copy()

        del a['name']
        del b['name']

        inner_value = 0.

        for col in a.keys():
            inner_value += (a[col] - b[col])**2

        return math.sqrt(inner_value)

    def neighbors(self, others):
        res = []
        for other in others:
            if other is self:
                continue
            res.append((other.name, self - other))
        return sorted(res, key=lambda x: x[1])

    def __repr__(self):
        return self.name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    libraries = db.relationship('Library', secondary=user_library)



    def __repr__(self):
        return self.name


class Library(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    games = db.relationship('Game', secondary=game_library)
    users = db.relationship('User', secondary=user_library)

    def recommend(self):
        others = Game.query.all()
        best = []
        res = []
        for game in self.games:
            for other in others:
                if game is other:
                    continue
                res.append((other.name, game - other))
            result = (sorted(res, key=lambda x: x[1]))
            best.append(result[0])
        print (result)
        return "You would like {first}, {second}, {third}".format(first=best[random.randint(0,len(best))], second =best[random.randint(0, len(best))], third=best[random.randint(0, len(best))])

    def __repr__(self):
        return self.name


@manager.command
def neighbors():
    games = Game.query.all()
    records = {}
    for game in games:
        records[game.name] = dict(game.neighbors(games))

    import pandas as pd
    df = pd.DataFrame(records)
    from IPython import embed
    embed()


if __name__ == '__main__':
    print(app.config['INVENTORY_FILE'])
    db.create_all()
    session = db.session
    if not session.query(Genre).count():
        session.add_all([
            Level(name='Novice', skill=1), Level(name='Intermediate', skill=2),
            Level(name='Expert', skill=3)
        ])
        session.add_all([Stars(1), Stars(2), Stars(3)])

        with open(app.config['INVENTORY_FILE'], 'r') as f:
            inventory = yaml.load(f)

            genres = set([g['genre'] for g in inventory])
            for genre in genres:
                session.add(Genre(name=genre.title()))
            session.commit()

            for src in inventory:
                game = Game(
                    name=src['name'],
                    level=Level.query.filter_by(skill=src['level']).one(),
                    genre=Genre.query.filter_by(name=src['genre']).one(),
                    duration=src['duration'],
                    min_player=src['min_player'],
                    max_player=src['max_player'])
                session.add(game)
        session.commit()

    for model in (Game, Level, Stars, Genre, User):
        admin.add_view(ExportableModelView(model, db.session))

    admin.add_view(LibraryModelView(Library, db.session))

    manager.run()
