from flask import render_template, flash, redirect, request, Response, jsonify
from arcadia_admin import app, db, models, theGameDB, ScanRoms
from forms import PlatformForm
from threading import Thread
import glob
import os
import time


scanner = None


class ScanRoms(Thread):
	file_names = []
	total_games_count = 0
	games_processed_count = 0
	file_extension = 'zip'
	platform_id = 0

	def __init__(self, scan_path='/', file_extension='zip', platform_id=0):
		Thread.__init__(self)

		self.file_extension = file_extension
		self.file_names = glob.glob(os.path.join(scan_path, '*.' + self.file_extension))
		self.platform_id = platform_id

	def run(self):
		platform = models.Platform.query.get(self.platform_id)
		games = platform.games
		self.total_games_count = games.count()

		for g in games:
			self.games_processed_count += 1
			game_full_file_name = g.file_name + '.' + self.file_extension
			for f in self.file_names:
				f = os.path.basename(f)
				# print game_full_file_name + " -- " + f
				if game_full_file_name == f:
					g.active = True
					break
				else:
					g.active = False

			db.session.add(g)
			db.session.commit()


@app.before_request
def before_request():
	# runs before any request
	print "request"


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


@app.route('/')
@app.route('/index')
def index():
	platforms = models.Platform.query.all()
	return render_template("index.html",
						   title='Home',
						   platforms=platforms)


@app.route('/platform')
def platform_view_all():
	platforms = models.Platform.query.all()

	return render_template("platform_view_all.html", title="Platforms", platforms=platforms)


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

	return render_template('platform_edit_form.html',
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

		return render_template("platform_view.html", title=page_title, platform=platform, games=games)


@app.route('/platform/<platform_id>/_rom_scan')
def platform_rom_scan(platform_id):

	platform = models.Platform.query.get_or_404(platform_id)
	rom_path = platform.roms_path
	extension = platform.extension
	global scanner

	if scanner is None:
		scanner = ScanRoms(scan_path=rom_path, file_extension=extension, platform_id=platform_id)
		scanner.start()
		return jsonify(status='running', total_files=scanner.total_games_count, files_processed=scanner.games_processed_count)
	elif scanner.is_alive():
		return jsonify(status='running', total_files=scanner.total_games_count, files_processed=scanner.games_processed_count)
	else:
		scanner = None
		return jsonify(status='ended')







