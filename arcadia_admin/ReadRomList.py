__author__ = 'Ashley'
from threading import Thread
from arcadia_admin import db, models, theGameDB
import xml.etree.ElementTree as ET
import os

class Generic_XML_List(Thread):
	total_games_count = 0
	games_processed_count = 0

	def __init__(self, xml_file_path=' ', platform_id=0):
		Thread.__init__(self)

		self.xml_file_path = xml_file_path
		self.tree = ET.parse(self.xml_file_path)
		self.platform_id = platform_id
		# self.total_games_count = self.tree.xpath("count(//game)")

	def run(self):
		for gameNode in self.tree.iter('game'):
			game_file_name = gameNode.get('name')
			game_name = gameNode.find('description').text

			if gameNode.find('manufacturer') is not None:
				publisher = gameNode.find('manufacturer').text
			else:
				publisher = ''

			new_game = models.Game(file_name=game_file_name, platform_id=self.platform_id, name=game_name, publisher=publisher, active=False)
			db.session.merge(new_game)
			self.games_processed_count += 1

		db.session.commit()
