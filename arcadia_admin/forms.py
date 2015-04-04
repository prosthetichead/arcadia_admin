from flask_wtf import Form
from wtforms.fields import StringField, BooleanField, TextAreaField, IntegerField, SelectField, FileField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired


class PlatformForm(Form):
	name = StringField('Platform Name', validators=[DataRequired()])
	desc = TextAreaField('Description')
	icon = HiddenField('Icon File', default='Default_Platform', validators=[DataRequired()])
	alias = StringField('Alias')
	emu_path = StringField('Emulator Path')
	roms_path = StringField('Roms Path')
	rom_extension = StringField('Roms Extension')
	load_string = StringField('Emulator Load String')
	videos_path = StringField('Videos Path')
	images_path = StringField('Images Path')
	active = BooleanField('Platform Active', default=False)


class FilterForm(Form):
	name = StringField('Filter Name', validators=[DataRequired()])
	filter_string = TextAreaField('Filter String')
	icon = HiddenField('Icon File', default='Default_Platform', validators=[DataRequired()])
	

class GameForm(Form):
	name = StringField('Game Name', validators=[DataRequired()])
	# filename = StringField('Game Filename', validators=[DataRequired()])
	desc = TextAreaField('Description')
	release_year = StringField('Release Year')
	publisher = StringField('Publisher')
	developer = StringField('Developer')
	genres = SelectMultipleField('Genres', coerce=int)


class RegionForm(Form):
	name = StringField('Region Name', validators=[DataRequired()])
	abbreviation = StringField('Region Abbreviation', validators=[DataRequired()])
	alt_names = StringField('Alternative Names')


class GenreForm(Form):
	name = StringField('Genre Name', validators=[DataRequired()])
	alt_names = StringField('Alternative Names')


class GameOnlineSearch(Form):
	provider = SelectField('Online Provider')
	search_title = StringField('Search')
	games_results = SelectField('Game Search Results')