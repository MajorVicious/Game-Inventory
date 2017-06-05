import requests
import untangle

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


	def save(self, *args, **kwargs):
		pass


def ids_generator():
	return list(range(1, 5))



for ids in ids_generator():
	r = requests.get('https://www.boardgamegeek.com/xmlapi/boardgame/{}?stats=1'.format(ids))
	doc = untangle.parse(r.text)
	chunk = [BoardGame(g) for g in doc.boardgames.boardgame]
	for game in chunk:
		print(game.name, game.year_published, game.mechanics, game.categories)
		game.save()







