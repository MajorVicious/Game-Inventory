from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import datetime
import yaml

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'CHANGEME'
db = SQLAlchemy(app)
admin = Admin(app, name='games', template_mode='bootstrap3', url='/')


class ExportableModelView(ModelView):
    can_export = True


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

    stars_id = db.Column(db.Integer, db.ForeignKey('stars.id'))
    stars = db.relationship(Stars)


if __name__ == '__main__':
    db.create_all()
    session = db.session
    if not session.query(Genre).count():
        session.add_all([
            Level(name='Novice', skill=1), Level(name='Intermediate', skill=2),
            Level(name='Expert', skill=3)
        ])
        session.add_all([Stars(1), Stars(2), Stars(3)])

        with open('../inventory.yml', 'r') as f:
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

    for model in (Game, Level, Stars, Genre):
        admin.add_view(ExportableModelView(model, db.session))

    app.run(host='0.0.0.0', port=8080, debug=True)
