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
	gamedb_id = SelectField('GamesDB ID', coerce=str)

	active = BooleanField('Platform Active', default=False)