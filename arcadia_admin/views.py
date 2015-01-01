from flask import render_template, flash, redirect, request, Response, jsonify
from arcadia_admin import app, db, models, theGameDB, ScanRoms, ReadRomList
from forms import PlatformForm
import os
from werkzeug import utils
from uuid import uuid4


scanner = None


@app.before_request
def before_request():
	# runs before any request
	print "request"


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


@app.route('/')
@app.route('/index')
@app.route('/platform')
def platform_view_all():
	platforms = models.Platform.query.all()

	return render_template("platforms.html", title="Platforms", platforms=platforms)


@app.route('/platform/new', defaults={'platform_id': None}, methods=['GET', 'POST'])
@app.route('/platform/<platform_id>/edit', methods=['GET', 'POST'])
def platform_edit_form(platform_id):
	form = PlatformForm()

	form.gamedb_id.choices = theGameDB.gameDB_platform_choices.iteritems()

	if platform_id is not None:  # get existing platform data and fill in the boxes
		platform = models.Platform.query.get_or_404(platform_id)
		if platform is None:
			return redirect('/platform')
	else:
		platform = models.Platform(name='')

	if form.validate_on_submit():
		platform.name = form.name.data
		platform.desc = form.desc.data
		if form.gamedb_id.data != 'New Platform':
			platform.gamedb_id = form.gamedb_id.data
		platform.active = form.active.data

		platform.alias = form.alias.data
		platform.icon_id = form.icon.data
		platform.extension = form.rom_extension.data
		platform.roms_path = form.roms_path.data

		db.session.add(platform)
		db.session.commit()
		flash('platform name ="%s", active=%s' % (form.name.data, str(form.active.data)))
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


@app.route('/platform/upload_rom_xml', methods=['POST'])
def upload_rom_xml():
	f = request.files['file']
	# TODO: Check if the file is one of the allowed types/extensions (check its XML)
	# Make the filename safe, remove unsupported chars
	filename = str(uuid4())  # utils.secure_filename(f.filename)
	f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	return jsonify(result='OK', filename=filename)


@app.route('/platform/<platform_id>/_load_rom_xml/<file_name>')
def load_rom_xml(platform_id, file_name):
	f = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
	readRomList = ReadRomList.Generic_XML_List(xml_file_path=f, platform_id=platform_id)
	readRomList.start()
	return jsonify(result='OK')


@app.route('/platform/<platform_id>/_rom_scan')
def platform_rom_scan(platform_id):

	platform = models.Platform.query.get_or_404(platform_id)
	rom_path = platform.roms_path
	extension = platform.extension
	global scanner

	if scanner is None:
		scanner = ScanRoms.ScanRoms(scan_path=rom_path, file_extension=extension, platform_id=platform_id)
		scanner.start()
		return jsonify(status='running', total_games=scanner.total_games_count, games_processed=scanner.games_processed_count)
	elif scanner.is_alive():
		return jsonify(status='running', total_games=scanner.total_games_count, games_processed=scanner.games_processed_count)
	else:
		scanner = None
		return jsonify(status='ended')








