from flask import render_template, flash, redirect, request, Response, jsonify
from arcadia_admin import app, db, models, AccessOnlineDatabases, ScanRoms, ReadGameList
from forms import PlatformForm, RegionForm
import os
from werkzeug import utils
from uuid import uuid4


scanner = None
readGameList = None


@app.before_request
def before_request():
	# runs before any request
	print "request"


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
	return render_template("platforms.html", title="Platforms", platforms=platforms)

@app.route('/region')
def regions_view_all():
	regions = models.Regions.query.all()
	return render_template("regions.html", title="Regions", regions=regions)


@app.route('/region/new', defaults={'region_id': None}, methods=['GET', 'POST'])
@app.route('/region/<region_id>/edit', methods=['GET', 'POST'])
def region_edit_form(region_id):
	form = RegionForm()

	if region_id is not None:
		region = models.Regions.query.get_or_404(region_id)
	else:
		region = models.Regions(region_name='')

	if form.validate_on_submit():
		region.region_name = form.name.data
		region.region_abbreviation = form.abbreviation.data
		region.alt_names = form.alt_names.data





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

		db.session.add(platform)
		db.session.commit()
		flash('platform "%s" updated' % (form.name.data) )

		return redirect('/platform')

	return render_template('platform_edit.html',
						   title='Platform ' + str(platform.name),
						   platform=platform,
						   form=form)


@app.route('/platform/<platform_id>')
def platform_view(platform_id):
	sort = request.args.get('sort', default='name')
	order = request.args.get('order', default='asc')  # desc
	platform = models.Platform.query.get_or_404(platform_id)
	try:
		sort_by = getattr(models.Game, sort)
		sort_order_by = getattr(sort_by, order)
	except AttributeError, e:
		print e
		return render_template('404.html'), 404
	else:
		games = db.session.query(models.Game). \
			filter(models.Game.platform_id == platform_id). \
			order_by(sort_order_by()).all()

		page_title = platform.name

		return render_template("platform.html", title=page_title, platform=platform, games=games)


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


@app.route('/platform/<platform_id>/_delete_games', methods=['GET'])
def delete_games(platform_id):
	game_id = request.args.get('game_id')
	try:
		if game_id == '__ALL':
			db.session.query(models.Game).filter(models.Game.platform_id == platform_id).delete(
				synchronize_session=False)
		else:
			db.session.query(models.Game).filter((models.Game.platform_id == platform_id)
												& (models.Game.id == game_id)).delete(
				synchronize_session=False)

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
		scanner = ScanRoms.ScanRoms(scan_path=rom_path, file_extension=extension, platform_id=platform_id)
		scanner.start()
		return jsonify(status='running', total_games=scanner.total_games_count,
					   games_processed=scanner.games_processed_count)
	elif scanner.is_alive():
		return jsonify(status='running', total_games=scanner.total_games_count,
					   games_processed=scanner.games_processed_count)
	else:
		scanner = None
		return jsonify(status='ended')








