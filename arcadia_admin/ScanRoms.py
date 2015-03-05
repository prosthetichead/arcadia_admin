from arcadia_admin import db, models, AccessOnlineDatabases
from threading import Thread
import glob
import os
import hashlib

class ScanRomsAvailable(Thread):

	total_games_count = 0
	games_processed_count = 0
	file_extension = 'zip'
	platform_id = 0

	def __init__(self, scan_path='/', file_extension='zip', platform_id=0):
		Thread.__init__(self)

		self.file_extension = file_extension
		self.file_names = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(os.path.join(scan_path, '*.*'))]
		self.platform_id = platform_id

	def run(self):
		platform = models.Platform.query.get(self.platform_id)
		games = platform.games
		self.total_games_count = games.count()

		for g in games:
			self.games_processed_count += 1
			if g.file_name in self.file_names:
				g.active = True
			else:
				g.active = False
			db.session.add(g)
			db.session.commit()


class ScanRomsAddAll(Thread):

	file_extension = 'zip'
	file_names = []
	games_processed_count = 0
	total_games_count = 0
	platform_id = 0

	def __init__(self, scan_path='/', file_extension='zip', platform_id=0):
		Thread.__init__(self)

		self.file_extension = file_extension
		self.file_names = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(os.path.join(scan_path, '*.*'))]
		self.platform_id = platform_id

	def run(self):
		for f in self.file_names:
			self.games_processed_count += 1
			game_id = hashlib.md5(self.platform_id + f.lower()).hexdigest()
			game = models.Game.query.get(game_id)
			if game is None:
				game = models.Game(file_name=f, id=game_id, name=f, active=True, platform_id=self.platform_id)
				db.session.add(game)
				db.session.commit()