from flask_wtf import Form
from wtforms.fields import StringField, BooleanField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired


class PlatformForm(Form):
	name = StringField('Platform Name', validators=[DataRequired()])
	desc = TextAreaField('Description')
	icon = StringField('Icon File')
	alias = StringField('Alias')
	emu_path = StringField('Emulator Path')
	roms_path = StringField('Roms Path')
	rom_extension = StringField('Roms Extension')
	load_string = StringField('Emulator Load String')
	videos_path = StringField('Videos Path')
	images_path = StringField('Images Path')
	active = BooleanField('Platform Active', default=False)

class RegionForm(Form):
	name = StringField('Region Name', validators=[DataRequired()])
	abbreviation = StringField('Region Abbreviation', validators=[DataRequired()])
	alt_names = StringField('Alternative Names')

class GameOnlineSearch(Form):
	provider = SelectField('Online Provider')
	search_title = StringField('Search')
	games_results = SelectField('Game Search Results')