from arcadia_admin import db


class Platform(db.Model):
	__tablename__ = 'platforms'
	id = db.Column(db.Integer, primary_key=True)
	gamedb_id = db.Column(db.String(100))
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
	platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), primary_key=True)
	file_name = db.Column(db.String(255), primary_key=True)
	gamedb_id = db.Column(db.String(255))
	genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
	region_id = db.Column(db.String(255), default='NONE')
	crc = db.Column(db.String(255))
	game_load_string = db.Column(db.Text)
	name = db.Column(db.String(255))
	description = db.Column(db.Text)
	release_year = db.Column(db.Integer, default=0)
	rating = db.Column(db.String(255))
	players = db.Column(db.Integer, default=0)
	co_op = db.Column(db.Boolean())
	publisher = db.Column(db.String(255))
	developer = db.Column(db.String(255))
	users_stars = db.Column(db.Numeric)
	gamedb_stars = db.Column(db.Numeric)
	control_type = db.Column(db.String(255))
	active = db.Column(db.Boolean())
	favourite = db.Column(db.Boolean())
	clone_of = db.Column(db.String(255))
	seconds_played = db.Column(db.Integer)
	last_played = db.Column(db.Date)


class Genre(db.Model):
	__tablename__ = 'genres'
	id = db.Column(db.Integer, primary_key=True)
	genre_name = db.Column(db.String(255))
	alt_names = db.Column(db.String(4000))
	icon_id = db.Column(db.String(255))
	games = db.relationship('Game', backref='genre', lazy='dynamic')


class Filter(db.Model):
	__tablename__ = 'filters'	
	name = db.Column(db.String(100), primary_key=True)
	icon_id = db.Column(db.String(255))
	filter_string = db.Column(db.Text)

	def __repr__(self):
		return '<Filter Name: %r> <%r>' % (self.name, self.filter_string)
