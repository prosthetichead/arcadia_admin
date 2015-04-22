from flask import render_template, flash, redirect, request, Response, jsonify, send_from_directory
from arcadia_admin import app, db, models, AccessOnlineDatabases, ScanRoms, ReadGameList, ImageTools
from forms import PlatformForm, RegionForm, GameForm, GenreForm, FilterForm
import os
import json
import glob
import urllib2
import random
from werkzeug import utils
from uuid import uuid4
import platform
import re


scanner = None
readGameList = None


def get_order_by(sort='name', order='desc'):
	try:
		sort_by = getattr(models.Game, sort)
		sort_order_by = getattr(sort_by, order)

		return sort_order_by
	except AttributeError, e:
		print e
		return render_template('404.html'), 404

def get_filter_result(filter_id, platform_id='all'):

	try:
		filter = models.Filter.query.get_or_404(filter_id)
		if platform_id != "all":
			platform_filter = "platforms.id = " + str(platform_id)
		else:
			platform_filter = "1=1"

		sql = """select distinct
				games.name name, games.file_name, platforms.id platform_id, platforms.name platform_name, games.id id
				from games
				join platforms on games.platform_id = platforms.id
				left join game_genres on games.id = game_genres.game_id
				left join genres on game_genres.genre_id = genres.id
				left join game_developers on games.id = game_developers.game_id
				left join companies developers on game_developers.developer_id = developers .id
				left join game_publishers on games.id = game_publishers.game_id
				left join companies publishers on game_publishers.publisher_id = publishers.id
				where games.active = 1
				and ({0}) and ({1}) order by games.name """.format(platform_filter, filter.filter_string)

		return db.engine.execute(sql).fetchall()
	except Exception, e:
		return None


@app.before_request
def before_request():
	# runs before any request
	print "--request--"


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


@app.route('/')
@app.route('/index')
def home():
	platforms = models.Platform.query.all()
	games = models.Game.query.all()
	filters = models.Filter.query.all()

	if db.session.query(models.Game).count() > 0:
		rand = random.randrange(0, db.session.query(models.Game).count())
		rgame = db.session.query(models.Game)[rand]
	else:
		rgame = None
	return render_template("index.html", platforms=platforms, games=games, filters=filters, rgame=rgame, title="Home")


@app.route('/<type>')
def attributes_view_all(type):
	try:
		dbModel = getattr(models, type)
		items = dbModel.query.all()
		return render_template("attributes.html", title="All " + type, items=items, type=type)
	except Exception, e:
		print e
		return render_template('404.html'), 404



@app.route('/Filter/new', defaults={'filter_id': None}, methods=['GET', 'POST'])
@app.route('/Filter/<filter_id>', methods=['GET', 'POST'])
def filter_edit_form(filter_id):
	form = FilterForm()
	filter_result = None

	if filter_id is not None:
		filter = models.Filter.query.get_or_404(filter_id)
		filter_result = get_filter_result(filter_id, 'all')
	else:
		filter = models.Filter(name='')
		

	if form.validate_on_submit():
		filter.name = form.name.data
		filter.icon = form.icon.data.upper()
		filter.filter_string = form.filter_string.data

		db.session.add(filter)
		db.session.commit()
		db.session.refresh(filter)
		return redirect('/Filter/'+ str(filter.id))
	elif filter.icon is not None:
		form.icon.data = filter.icon

	return render_template('filter_edit.html',
						   title='Filter ' + str(filter.name),
						   filter=filter,
						   filter_result=filter_result,
						   form=form)


@app.route('/Genre/new', defaults={'genre_id': None}, methods=['GET', 'POST'])
@app.route('/Genre/<genre_id>/edit', methods=['GET', 'POST'])
def genre_edit_form(genre_id):
	form = GenreForm()

	if genre_id is not None:
		genre = models.Genre.query.get_or_404(genre_id)
	else:
		genre = models.Genre(name='')

	if form.validate_on_submit():
		genre.name = form.name.data
		genre.alt_names = form.alt_names.data

		db.session.add(genre)
		db.session.commit()

		return redirect('/genre')

	return render_template('genre_edit.html',
						   title='Genre Edit ' + str(genre.name),
						   genre=genre,
						   form=form)


@app.route('/Game/<game_id>/edit', methods=('GET', 'POST'))
def game_edit(game_id):
	form = GameForm()

	form.genres.choices = models.Genre.query.with_entities(models.Genre.id, models.Genre.name) \
		.order_by(models.Genre.name.asc())

	game = models.Game.query.get_or_404(game_id)
	platform = game.platform

	if form.validate_on_submit():
		game.name = form.name.data
		game.desc = form.desc.data
		game.id_genres = form.genres.data
		db.session.add(game)
		db.session.commit()
		return redirect("/Game/%s" % (game_id))
	else:
		form.genres.default = game.id_genres
		form.process()

	return render_template("game_edit.html", title="Game Edit", platform=platform, game=game, form=form)


@app.route('/Platform/new', defaults={'platform_id': None}, methods=['GET', 'POST'])
@app.route('/Platform/<platform_id>/edit', methods=['GET', 'POST'])
def platform_edit_form(platform_id):
	form = PlatformForm()

	if platform_id is not None:  # get existing platform data and fill in the boxes
		platform = models.Platform.query.get_or_404(platform_id)
	else:
		platform = models.Platform(name='')

	if form.validate_on_submit():
		platform.name = form.name.data
		platform.desc = form.desc.data
		platform.active = form.active.data
		platform.alias = form.alias.data
		platform.icon = form.icon.data.upper()
		platform.extension = form.rom_extension.data
		platform.roms_path = form.roms_path.data
		platform.images_path = form.images_path.data
		platform.videos_path = form.videos_path.data
		platform.load_string = form.load_string.data
		platform.emu_path = form.emu_path.data

		db.session.add(platform)
		db.session.commit()

		return redirect('/')
	elif platform.icon is not None:
		form.icon.data = platform.icon


	return render_template('platform_edit.html',
						   title='Platform Edit ' + str(platform.name),
						   platform=platform,
						   form=form)


@app.route('/Game/<game_id>')
def game_view(game_id):
	game = models.Game.query.get_or_404(game_id)
	platform = game.platform

	return render_template("game.html", title="Game", platform=platform, game=game)


@app.route('/Platform/<platform_id>')
def platform_view(platform_id=1):
	sort = request.args.get('sort', default='name')
	order = request.args.get('order', default='asc')  # desc
	page = int(request.args.get('page', default=1))
	per_page = int(request.args.get('per_page', default=100))

	platform = models.Platform.query.get_or_404(platform_id)

	sort_order_by = get_order_by(sort, order)
	games = platform.games.order_by(sort_order_by()).paginate(page, per_page, False)
	page_title = platform.name
	return render_template("platform.html", title=page_title, platform=platform, games=games)


@app.route('/<type>/<id>')
def view_attribute(type, id):
	sort = request.args.get('sort', default='name')
	order = request.args.get('order', default='asc')  # desc
	page = int(request.args.get('page', default=1))
	per_page = int(request.args.get('per_page', default=100))

	dbModel = getattr(models, type)
	item = dbModel.query.get_or_404(id)

	sort_order_by = get_order_by(sort, order)
	games = item.games.order_by(sort_order_by()).paginate(page, per_page, False)
	page_title = item.name
	return render_template("view_attribute.html", type=type, title=page_title, item=item, games=games)


@app.route('/Platform/<platform_id>/_load_game_list', methods=['GET', 'POST'])
def load_game_list(platform_id):
	if request.method == 'POST':
		f = request.files['file']

		file_type = os.path.splitext(f.filename)[1]
		filename = str(uuid4())  # utils.secure_filename(f.filename)
		f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		return jsonify(result='OK', filename=filename, file_type=file_type)

	elif request.method == 'GET':
		filename = request.args.get('filename')
		filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file_type = request.args.get('file_type').lower()

		global readGameList

		if readGameList is None:
			if file_type == '.xml':
				readGameList = ReadGameList.Generic_XML_List(xml_file_path=filename, platform_id=platform_id)
				readGameList.start()
				return jsonify(status='running', total_games_count=readGameList.total_games_count,
							   games_processed_count=readGameList.games_processed_count)

		elif readGameList.is_alive():
			return jsonify(status='running', total_games_count=readGameList.total_games_count,
						   games_processed_count=readGameList.games_processed_count)

		else:
			readGameList = None
			return jsonify(status='ended')


@app.route('/Platform/<platform_id>/_upload_game_file', methods=['POST'])
def upload_game_file(platform_id):
	"""Upload a game rom file to the platforms rom folder."""

	try:
		f = request.files['file']
		platform = models.Platform.query.get_or_404(platform_id)

		file_type = os.path.splitext(utils.secure_filename(f.filename))[1][1:]
		filename_noExtension = os.path.splitext(utils.secure_filename(f.filename))[0]
		full_filename = utils.secure_filename(f.filename)

		if file_type == platform.extension:  # is this the file type we are using for roms?
			if not os.path.exists(platform.roms_path):
				os.makedirs(platform.roms_path)

			f.save(os.path.join(platform.roms_path, full_filename))
			game_id = ScanRoms.addGameRom(str(platform.id), filename_noExtension)

			return jsonify(result='OK', file_name=filename_noExtension, file_type=file_type, game_id=game_id)

		else:
			return jsonify(result='ERROR', file_name=filename_noExtension, file_type=file_type,
						   msg='Wrong file extension for platforms settings. Received ' + file_type + ' should be ' + platform.extension)

	except Exception, e:
		return jsonify(result='ERROR', file_name=filename_noExtension, file_type=file_type, msg=str(e))


@app.route('/Game/<game_id>/img/<image_type>')
def send_game_image(game_id, image_type):
	game = models.Game.query.get_or_404(game_id)
	platform = game.platform

	if platform.images_path is not None:
		image_type_path = os.path.join(platform.images_path, image_type)
		if os.path.exists(image_type_path):
			filename = ""

			for name in glob.glob(os.path.join(image_type_path, game.file_name + '.*')):
				filename = os.path.basename(name)

			if filename != "":
				return send_from_directory(image_type_path, filename)
			elif filename == "" and image_type != 'fanart':
				return app.send_static_file('img/placeholder.jpg')

	return ""


@app.route('/Game/<game_id>/vid')
def send_game_video(platform_id, game_id):
	game = models.Game.query.get_or_404(game_id)
	platform = game.platform

	if platform.videos_path is not None:

		if os.path.exists(platform.videos_path):
			filename = ""
			for name in glob.glob(os.path.join(platform.videos_path, game.file_name + '.*')):
				filename = os.path.basename(name)
			return send_from_directory(platform.videos_path, filename)

	return ""





@app.route('/_delete_games', methods=['GET'])
def delete_games():
	game_id = request.args.get('game_id', default=0)
	platform_id = request.args.get('platform_id', default=0)
	try:
		if game_id == '__ALL':
			db.session.query(models.Game).filter(models.Game.platform_id == platform_id).delete(
				synchronize_session=False)
		else:
			db.session.query(models.Game).filter(models.Game.id == game_id).delete(synchronize_session=False)

		db.session.commit()
		return jsonify(result='OK')
	except Exception, e:
		return jsonify(result='ERROR', msg=e.message)


@app.route('/_delete', methods=['GET'])
def delete():
	id = request.args.get('item_id', default=0)
	type = request.args.get('type', default='')
	try:
		dbModel = getattr(models, type)
		db.session.query(dbModel).filter(dbModel.id == id).delete(synchronize_session=False)
		db.session.commit()
		return jsonify(result='OK')
	except Exception, e:
		return jsonify(result='ERROR', msg=str(e))


@app.route('/platform/<platform_id>/_rom_scan')
def platform_rom_scan(platform_id):
	platform = models.Platform.query.get_or_404(platform_id)
	rom_path = platform.roms_path
	extension = platform.extension
	global scanner

	if scanner is None:
		scanner = ScanRoms.ScanRomsAvailable(scan_path=rom_path, file_extension=extension, platform_id=platform_id)
		scanner.start()
		return jsonify(status='running', total_games=scanner.total_games_count,
					   games_processed=scanner.games_processed_count)
	elif scanner.is_alive():
		return jsonify(status='running', total_games=scanner.total_games_count,
					   games_processed=scanner.games_processed_count)
	else:
		scanner = None
		return jsonify(status='ended')


#
# Add all games in the roms folder and activate them
#
@app.route('/platform/<platform_id>/_rom_scan_add_all')
def platform_rom_scan_add_all(platform_id):
	platform = models.Platform.query.get_or_404(platform_id)
	rom_path = platform.roms_path
	extension = platform.extension
	global scanner

	if scanner is None:
		scanner = ScanRoms.ScanRomsAddAll(scan_path=rom_path, file_extension=extension, platform_id=platform_id)
		scanner.start()
		return jsonify(status='running', total_games=scanner.total_games_count,
					   games_processed=scanner.games_processed_count)
	elif scanner.is_alive():
		return jsonify(status='running', total_games=scanner.total_games_count,
					   games_processed=scanner.games_processed_count)
	else:
		scanner = None
		return jsonify(status='ended')


@app.route('/_online_search')
def game_online_search():
	search_string = request.args.get('search', default=" ")
	provider = request.args.get('provider', default=" ")

	print 'online_search: ' + provider

	if provider == 'thegamedb':
		result = AccessOnlineDatabases.search_thegamesdb_game(search_string)
	elif provider == 'giantbomb':
		result = AccessOnlineDatabases.search_giantbomb_game(search_string)
	else:
		result = None

	return Response(json.dumps(result), mimetype='application/json')


@app.route('/_game_image_search_online')
def game_image_search_online():
	provider_game_id = request.args.get('provider_game_id', default="1")
	provider = request.args.get('provider', default="thegamedb")

	print "game_image_search: " + provider

	if provider == 'thegamedb':
		result = AccessOnlineDatabases.get_thegamesdb_game_images(provider_game_id)
	elif provider == 'giantbomb':
		result = AccessOnlineDatabases.get_giantbomb_game_images(provider_game_id)
	else:
		result = None

	return Response(json.dumps(result), mimetype='application/json')


@app.route('/_update_from_online/game/<game_id>')
def update_from_online(game_id):
	provider_game_id = request.args.get('provider_game_id', default="0")
	provider = request.args.get('provider', default="thegamedb")

	game = models.Game.query.get_or_404(game_id)

	if provider == 'giantbomb':
		result = AccessOnlineDatabases.get_giantbomb_game(provider_game_id)
		game.name = result['name']
		game.description = result['desc']
		game.str_genres = result['genres']
		game.str_developers = result['developers']
		game.str_publishers = result['publishers']
		db.session.commit()
	elif provider == 'thegamedb':
		print AccessOnlineDatabases.get_thegamesdb_game_images(provider_game_id)

	return jsonify(status='complete')


@app.route('/_assets/<asset_type>')
def get_assets_list(asset_type):
	assets_path = app.config['ASSETS_FOLDER']
	assets_path = os.path.join(assets_path, asset_type)
	if os.path.exists(assets_path):
		filelist = glob.glob(os.path.join(assets_path, "*.png"))
		asset_details = []
		for file_name in filelist:

			file_name = os.path.basename(file_name)
			file_name, extension = os.path.splitext(file_name)
			asset_details.append({'file_name': file_name, 'asset_url': '/_assets/' + asset_type + '/' + file_name, 'extension': extension})

		return Response(json.dumps(asset_details), mimetype='application/json')

	return jsonify(status='error', assets_path=assets_path)


@app.route('/_assets/<asset_type>/<asset_file_name>')
def get_asset(asset_type, asset_file_name):
	asset_path = os.path.join(app.config['ASSETS_FOLDER'], asset_type)
	if asset_type.lower() == 'icons':
		return send_from_directory(asset_path, asset_file_name + '.png')



@app.route('/_update_image_from_online/game/<game_id>')
def update_image_from_online(game_id):
	game = models.Game.query.get_or_404(game_id)
	image_url = request.args.get('image_url', default=" ")
	image_type = request.args.get('type', default=" ")
	original_extention = extension = os.path.splitext(image_url)[1]

	path = os.path.join(game.platform.images_path, image_type)
	# test if directory exists if not create it
	if not os.path.exists(path):
		os.makedirs(path)
	# test if any files exist in the directory with the same file name (any extension)
	filelist = glob.glob(os.path.join(path, game.file_name + ".*"))
	for f in filelist:
		os.remove(f)

	req = urllib2.Request(image_url, headers={'User-Agent': "arcadia_admin"})
	f = urllib2.urlopen(req)
	image_full_path = os.path.join(path, game.file_name + original_extention)
	with open(image_full_path, "wb") as code:
		code.write(f.read())

	if ImageTools.is_jpg_progresive(image_full_path):
		ImageTools.convert_to_jpg(image_full_path)

	return jsonify(status='complete')


@app.route('/controls')
def settings_inputs():
	return render_template("settings_controls.html", title="Arcadia Controls")

@app.route('/_file_browser')
def file_browser():
	path = request.args.get('path', default='')
	print path
	return_items = []


	if platform.system() == 'Windows':

		if not os.path.isdir(path):
			drives = re.findall(r"[A-Z]+:.*$", os.popen("mountvol /").read(), re.MULTILINE)
			for drive in drives:
				return_items.append({'file_name': drive, 'path': drive, 'type': 'dir'})
		else:
			for filename in os.listdir(path):
				if os.path.isdir(os.path.join(path, filename)):
					return_items.append({'file_name': filename, 'path': os.path.join(path, filename), 'type': 'dir'})
			for filename in os.listdir(path):
				if os.path.isfile(os.path.join(path, filename)):
					return_items.append({'file_name': filename, 'path': os.path.join(path, filename), 'type': 'file'})

	return Response(json.dumps(return_items), mimetype='application/json')