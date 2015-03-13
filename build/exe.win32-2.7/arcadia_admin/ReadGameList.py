__author__ = 'Ashley'
from threading import Thread
from arcadia_admin import db, models, AccessOnlineDatabases
import xml.etree.ElementTree as ET
import os
import re
import time
import hashlib


class Generic_XML_List(Thread):
	total_games_count = 0
	games_processed_count = 0

	def __init__(self, xml_file_path=' ', platform_id=0):
		Thread.__init__(self)

		self.xml_file_path = xml_file_path
		self.tree = ET.parse(self.xml_file_path)
		self.platform_id = platform_id
		self.total_games_count = len(self.tree.findall('game'))

	def run(self):

		re_brackets = re.compile(r"\((.*?)\)")

		for gameNode in self.tree.iter('game'):

			# Game Name and File Name
			game_file_name = gameNode.get('name')
			if gameNode.find('description') is not None:
				game_name = gameNode.find('description').text
			else:
				game_name = game_file_name

			# Regions
			game_regions = []
			if gameNode.find('release') is not None:
				for releaseNode in gameNode.iter('release'):
					game_regions.append(releaseNode.get('region'))
			else:
				game_regions = []

			game_genres = []
			if gameNode.find('genre') is not None:
				genres = gameNode.find('genre').text.split('/')
				game_genres = genres

			# Publisher
			if gameNode.find('manufacturer') is not None:
				publisher = gameNode.find('manufacturer').text
			else:
				publisher = ''


			# Generate ID based on platform ID and Game File Name
			game_id = hashlib.md5(self.platform_id + game_file_name.lower()).hexdigest()

			game = models.Game.query.filter(models.Game.id == game_id).first()
			if game is None:
				game = models.Game(id=game_id, active=False, platform_id=self.platform_id)
				db.session.add(game)

			game.name = game_name
			game.file_name = game_file_name
			game.platform_id = self.platform_id

			db.session.merge(game)
			game.str_regions = game_regions
			game.str_genres = game_genres

			self.games_processed_count += 1
		db.session.commit()


