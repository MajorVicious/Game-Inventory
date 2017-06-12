import requests
import untangle
import time
import csv
import os

class BoardGame:
	def __init__(self, node):
		self._node = node

	@property
	def name(self):
		if isinstance(self._node.name, (list, tuple)):
			for n in self._node.name:
				if n._attributes['primary'] == 'true':
					return n.cdata
		else:
			return self._node.name.cdata

	@property
	def year_published(self):
		return int(self._node.yearpublished.cdata)

	@property
	def mechanics(self):
		return [x.cdata for x in self._node.boardgamemechanic]

	@property
	def categories(self):
		return [x.cdata for x in self._node.boardgamecategory]

	@property
	def min_player(self):
		return int(self._node.minplayers.cdata)

	@property
	def max_player(self):
		return int(self._node.maxplayers.cdata)
	
	@property
	def playing_time(self):
    		return int(self._node.playingtime.cdata)
	
	@property
	def age(self):
    		return int(self._node.age.cdata)
	@property
	def thumbnail(self):
 		return self._node.thumbnail.cdata

	@property
	def rating(self):
    		return float(self._node.statistics.ratings.average.cdata)

	@property
	def weight(self):
		return float(self._node.statistics.ratings.averageweight.cdata)

	@property
	def description(self):
		text = self._node.description.cdata
		return text

	def features(self):
		return {'name': self.name,
				'year_published': self.year_published,
				'mechanics': self.mechanics,
				'categories': self.categories,
				'min_player': self.min_player,
				'max_player': self.max_player,
				'playing_time': self.playing_time,
				'age': self.age,
				'thumbnail': self.thumbnail,
				'rating': self.rating,
				'weight': self.weight,
				'description': self.description}


def save(game):
	if os.path.exists('inventory.csv'):
		with open('inventory.csv', 'r') as f:
			reader = csv.DictReader(f)
			inventory = []
			for row in reader:
				inventory.append(row)
				
				
	else:
		inventory = []

	updated = False
	for existing in inventory:
		if existing['name'] == game.name:
			updated = True
			existing.update(game.features())

	if not updated:
		inventory.append(game.features())

	with open('inventory.csv', 'w') as f:
		fieldnames = (['name', 'year_published', 'mechanics', 'categories', 'min_player', 
		'max_player', 'playing_time', 'age', 'thumbnail', 'rating', 'weight', 'description'])
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		for game in inventory:
			writer.writerow(game)

def ids_generator(x, y):
	array = range(x, y)
	return list(array)


def request():
	z = 0
	x = 10
	y = x + 20
	while z < 5: 
		for ids in ids_generator(x, y):
			r = requests.get('https://www.boardgamegeek.com/xmlapi/boardgame/{}?stats=1'.format(ids))
			doc = untangle.parse(r.text)
			chunk = [BoardGame(g) for g in doc.boardgames.boardgame]
			for game in chunk:
				save(game)
		x = y
		y = x + 20
		z += 1
		print("Still {} to do.".format(5 - z))
		time.sleep(2)


request()






