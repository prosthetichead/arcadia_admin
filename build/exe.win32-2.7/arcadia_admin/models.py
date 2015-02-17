from arcadia_admin import db


class OnlineDatabase(db.Model):
	__tablename__ = 'online_databases'
	id = db.Column(db.String(32), primary_key=True)
	name = db.Column(db.String(255))
	api_key = db.Column(db.String(255))


class Platform(db.Model):
	__tablename__ = 'platforms'
	id = db.Column(db.Integer, primary_key=True)
	icon_id = db.Column(db.String(255))
	name = db.Column(db.String(255))
	desc = db.Column(db.String(4000))
	alias = db.Column(db.String(255))
	load_string = db.Column(db.String(4000))
	emu_path = db.Column(db.String(4000))
	roms_path = db.Column(db.String(4000))
	videos_path = db.Column(db.String(4000))
	images_path = db.Column(db.String(4000))
	extension = db.Column(db.String(64))
	active = db.Column(db.Boolean())
	games = db.relationship('Game', backref='platform', lazy='dynamic')
	games_active = db.relationship('Game', primaryjoin="and_(Platform.id==Game.platform_id, Game.active == True)",
									lazy='dynamic')


class Game(db.Model):
	__tablename__ = 'games'
	id = db.Column(db.String(32), primary_key=True)  # MD5 Hash of platform_id + file_name
	platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'))
	file_name = db.Column(db.String(255))
	game_load_string = db.Column(db.Text)
	name = db.Column(db.String(255))
	description = db.Column(db.Text)
	release_year = db.Column(db.Integer, default=0)
	rating = db.Column(db.String(255))
	players = db.Column(db.Integer, default=0)
	co_op = db.Column(db.Boolean())
	publisher = db.Column(db.String(255))
	developer = db.Column(db.String(255))
	favourite = db.Column(db.Boolean())
	stars = db.Column(db.Numeric)
	active = db.Column(db.Boolean())
	seconds_played = db.Column(db.Integer)
	last_played = db.Column(db.Date)
	clone_of = db.Column(db.String(32))

	def _find_or_create_regions(self, region=' '):
		q = Region.query.filter((Region.alt_names.like('%"' + region + '"%'))
								| (db.func.lower(Region.name) == db.func.lower(region))
								| (db.func.lower(Region.abbreviation) == db.func.lower(region)))
		r = q.first()
		if not r:
			r = Region(name=region, abbreviation=region)
		return r

	def _get_regions(self):
		return [x.name for x in self.regions]

	def _set_regions(self, value):
		# clear the list first
		while self.regions:
			del self.regions[0]
		# add new tags
		for regions in value:
			self.regions.append(self._find_or_create_regions(regions))

	str_regions = property(_get_regions,
							_set_regions,
							"Property str_region is a simple wrapper for regions relation")

	def _find_or_create_genres(self, genre=' '):
		q = Genre.query.filter((Genre.alt_names.like('%"' + genre + '"%'))
								| (db.func.lower(Genre.name) == db.func.lower(genre)))
		r = q.first()
		if not r:
			r = Genre(name=genre)
		return r

	def _get_genres(self):
		return [x.name for x in self.genres]

	def _set_genres(self, value):
		# clear the list first
		while self.genres:
			del self.genres[0]
		# add new tags
		for genres in value:
			self.genres.append(self._find_or_create_genres(genres))

	str_genres = property(_get_genres,
							_set_genres,
							"Property str_genres is a simple wrapper for genres relation")


GameGenres = db.Table('game_genres',
	db.Column('game_id', db.Integer, db.ForeignKey('games.id')),
	db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'))
)


class Genre(db.Model):
	__tablename__ = 'genres'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	alt_names = db.Column(db.String(4000))
	games = db.relationship("Game", secondary=GameGenres, backref="genres", lazy='dynamic')

GameRegions = db.Table('game_regions',
	db.Column('game_id', db.Integer, db.ForeignKey('games.id')),
	db.Column('region_id', db.Integer, db.ForeignKey('regions.id'))
)


class Region(db.Model):
	__tablename__ = 'regions'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	abbreviation = db.Column(db.String(10))
	alt_names = db.Column(db.String(4000))
	games = db.relationship("Game", secondary=GameRegions, backref="regions", lazy='dynamic')


class Filter(db.Model):
	__tablename__ = 'filters'	
	name = db.Column(db.String(100), primary_key=True)
	icon_id = db.Column(db.String(255))
	filter_string = db.Column(db.Text)

	def __repr__(self):
		return '<Filter Name: %r> <%r>' % (self.name, self.filter_string)

class Input(db.Model):
	__tablename__ = 'inputs'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	input_type = db.Column(db.String(100))
	keyboard_key_id = db.Column(db.Integer, default=0)
