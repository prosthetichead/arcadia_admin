from flask import render_template, flash, redirect, request, Response, jsonify, send_from_directory
from arcadia_admin import app, db, models, AccessOnlineDatabases, ScanRoms, ReadGameList
from forms import PlatformForm, RegionForm, GameForm, GenreForm
import os
import json
import glob
from werkzeug import utils
from uuid import uuid4


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


@app.before_request
def before_request():
	# runs before any request
	
	print "\n\n--request--"


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


@app.route('/')
@app.route('/index')
def home():
	return render_template("index.html", title="Home")


@app.route('/platform')
def platform_view_all():
	platforms = models.Platform.query.all()
	return render_template("platforms.html", title="All Platforms", platforms=platforms)


@app.route('/region')
def regions_view_all():
	regions = models.Region.query.all()
	return render_template("region.html", title="All Regions", regions=regions)


@app.route('/genre')
def genre_view_all():
	genres = models.Genre.query.all()
	return render_template("genres.html", title="All Genres", genres=genres)


@app.route('/region/new', defaults={'region_id': None}, methods=['GET', 'POST'])
@app.route('/region/<region_id>/edit', methods=['GET', 'POST'])
def region_edit_form(region_id):
	form = RegionForm()

	if region_id is not None:
		region = models.Region.query.get_or_404(region_id)
	else:
		region = models.Region(name='')

	if form.validate_on_submit():
		region.name = form.name.data
		region.abbreviation = form.abbreviation.data
		region.alt_names = form.alt_names.data

		db.session.add(region)
		db.session.commit()

		return redirect('/region')

	return render_template('region_edit.html',
						   title='Region Edit ' + str(region.name),
						   region=region,
						   form=form)


@app.route('/genre/new', defaults={'genre_id': None}, methods=['GET', 'POST'])
@app.route('/genre/<genre_id>/edit', methods=['GET', 'POST'])
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


@app.route('/platform/new', defaults={'platform_id': None}, methods=['GET', 'POST'])
@app.route('/platform/<platform_id>/edit', methods=['GET', 'POST'])
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
		platform.icon_id = form.icon.data
		platform.extension = form.rom_extension.data
		platform.roms_path = form.roms_path.data
		platform.images_path = form.images_path.data
		platform.videos_path = form.videos_path.data

		db.session.add(platform)
		db.session.commit()
		flash('platform "%s" updated' % (form.name.data))

		return redirect('/platform')

	return render_template('platform_edit.html',
						   title='Platform Edit ' + str(platform.name),
						   platform=platform,
						   form=form)


@app.route('/platform/<platform_id>')
def platform_view(platform_id=1):
	sort = request.args.get('sort', default='name')
	order = request.args.get('order', default='asc')  # desc
	page = int(request.args.get('page', default=1))
	per_page = int(request.args.get('per_page', default=100))

	platform = models.Platform.query.get_or_404(platform_id)

	sort_order_by = get_order_by(sort, order)
	games = models.Game.query.filter(models.Game.platform_id == platform_id). \
		order_by(sort_order_by()).paginate(page, per_page, False)
	page_title = platform.name
	return render_template("platform.html", title=page_title, platform=platform, games=games)


@app.route('/region/<region_id>')
def region_view(region_id):
	sort = request.args.get('sort', default='name')
	order = request.args.get('order', default='asc')  # desc
	page = int(request.args.get('page', default=1))
	per_page = int(request.args.get('per_page', default=100))

	region = models.Region.query.get_or_404(region_id)

	sort_order_by = get_order_by(sort, order)
	games = models.Game.query.filter(models.Game.regions.any(id=region_id)). \
		order_by(sort_order_by()).paginate(page, per_page, False)
	page_title = region.name
	return render_template("region.html", title=page_title, region=region, games=games)


@app.route('/genre/<genre_id>')
def genre_view(genre_id):
	sort = request.args.get('sort', default='name')
	order = request.args.get('order', default='asc')  # desc
	page = int(request.args.get('page', default=1))
	per_page = int(request.args.get('per_page', default=100))

	genre = models.Genre.query.get_or_404(genre_id)

	sort_order_by = get_order_by(sort, order)
	games = models.Game.query.filter(models.Game.genres.any(id=genre_id)). \
		order_by(sort_order_by()).paginate(page, per_page, False)
	page_title = genre.name
	return render_template("genre.html", title=page_title, genre=genre, games=games)


@app.route('/platform/<platform_id>/_load_game_list', methods=['GET', 'POST'])
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


@app.route('/platform/<platform_id>/game/<game_id>/edit', methods=('GET', 'POST'))
@app.route('/platform/<platform_id>/game/new', defaults={'game_id': None}, methods=['GET', 'POST'])
def game_edit(platform_id, game_id):
	form = GameForm()

	form.genres.choices = models.Genre.query.with_entities(models.Genre.id, models.Genre.name) \
		.order_by(models.Genre.name.asc())


	if game_id is not None:  # get existing platform data and fill in the boxes
		game = models.Game.query.get_or_404(game_id)
		platform = game.platform
	else:
		game = models.Platform(name='')
		platform = models.Platform.query.get_or_404(platform_id)

	if form.validate_on_submit():
		game.name = form.name.data
		game.desc = form.desc.data
		game.id_genres = form.genres.data
		db.session.add(game)
		db.session.commit()
		return redirect("/platform/%s/game/%s" % (platform_id, game_id))
	else:
		form.genres.default = game.id_genres
		form.process()


	return render_template("game_edit.html", title="Game Edit", platform=platform, game=game, form=form)


@app.route('/platform/<platform_id>/game/<game_id>/img/<image_type>')
def send_game_image(platform_id, game_id, image_type):
	game = models.Game.query.get_or_404(game_id)
	platform = game.platform

	if platform.images_path is not None:
		image_type_path = os.path.join(platform.images_path, image_type)
		if os.path.exists(image_type_path):
			filename = ""
			for name in glob.glob(os.path.join(image_type_path, game.file_name + '.*')):
				filename = os.path.basename(name)
			return send_from_directory(image_type_path, filename)

	return ""


@app.route('/platform/<platform_id>/game/<game_id>/vid')
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

@app.route('/platform/<platform_id>/game/<game_id>')
def game_view(platform_id, game_id):
	game = models.Game.query.get_or_404(game_id)
	platform = game.platform

	return render_template("game.html", title="Game", platform=platform, game=game)


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