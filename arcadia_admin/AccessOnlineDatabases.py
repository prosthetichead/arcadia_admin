__author__ = 'Ashley'
import requests
import xml.etree.ElementTree as ET
import urllib

thegamesdb_platform_choices = {0: "None Chosen"}
giantbomb_platform_choices = {0: "None Chosen"}
giantbomb_api_key = '4936b27215c2062d42539597b3732f99541a3223'

def refresh_giantbomb_platform_choices():
	r = requests.get('http://www.giantbomb.com/api/platforms/?api_key=4936b27215c2062d42539597b3732f99541a3223&sort=name:asc')
	platforms_tree = ET.fromstring(r.content)
	giantbomb_platform_choices.clear()
	giantbomb_platform_choices.update({0: "None Chosen"})
	for elem in platforms_tree.iter('platform'):
		pf_id = elem.find('id').text
		pf_name = elem.find('name').text
		giantbomb_platform_choices.update({pf_id: pf_name})
		print pf_name
	print "giantbomb platform choice refresh complete"


def refresh_thegamesdb_platform_choices():
	try:
		r = requests.get('http://thegamesdb.net/api/GetPlatformsList.php')
		platforms_tree = ET.fromstring(r.content)
		thegamesdb_platform_choices.clear()
		thegamesdb_platform_choices.update({0: "None Chosen"})
		for elem in platforms_tree.iter('Platform'):
			pf_id = elem.find('id').text
			pf_name = elem.find('name').text
			thegamesdb_platform_choices.update({pf_id: pf_name})
		print "thegamesdb platform choice refresh complete"
	except Exception, e:
		print "thegamesdb platform choice refresh Error"

def search_thegamesdb_game(value=" "):
	try:
		params = urllib.urlencode({'name': value})
		url = "http://thegamesdb.net/api/GetGamesList.php?%s" % params
		print url
		r = requests.get(url)
		games_tree = ET.fromstring(r.content)
		results = []
		for elem in games_tree.iter('Game'):
			id = elem.find('id').text
			name = elem.find('GameTitle').text
			platform = elem.find('Platform').text
			game = {'id': id, 'name': name, 'platform': platform}
			results.append(game)
		return results

	except Exception, e:
		print "thegamesdb platform choice refresh Error"

def search_giantbomb_game(value=" "):
	try:
		params = urllib.urlencode({'query': value})
		url = "http://www.giantbomb.com/api/search/?api_key=4936b27215c2062d42539597b3732f99541a3223&resources=game&sort=name:asc&%s" % params
		print url
		r = requests.get(url)
		games_tree = ET.fromstring(r.content)
		results = []
		for elem in games_tree.iter('game'):
			id = elem.find('id').text
			name = elem.find('name').text

			elem_platforms = elem.find('platforms')
			platform = ""
			for elem_platform in elem_platforms.iter('platform'):
				platform += "[" + elem_platform.find('name').text + "] "

			game = {'id': id, 'name': name, 'platform': platform}
			results.append(game)
		return results

	except Exception, e:
		print "thegamesdb platform choice refresh Error"


def get_giantbomb_game(online_game_id="6647"):
	url = "http://www.giantbomb.com/api/game/" + str(online_game_id) + "/?api_key=4936b27215c2062d42539597b3732f99541a3223"
	r = requests.get(url)
	game_tree = ET.fromstring(r.content)

	elem = game_tree.find('results')
	name = elem.find('name').text
	desc = elem.find('deck').text

	elem_genres = elem.find('genres')
	genres = []
	for elem_genre in elem_genres.iter('genre'):
		genre_name = elem_genre.find('name').text
		genres.append(genre_name)

	elem_developers = elem.find('developers')
	developers = []
	for elem_developer in elem_developers.iter('company'):
		developer_name = elem_developer.find('name').text
		developers.append(developer_name)

	elem_publishers = elem.find('publishers')
	publishers = []
	for elem_publisher in elem_publishers.iter('publisher'):
		p_name = elem_publisher.find('name').text
		print p_name
		publishers.append(p_name)

	game = {'name': name, 'genres': genres, 'desc': desc, 'developers': developers, 'publishers': publishers}
	return game


def get_thegamesdb_game_images(online_game_id="6647"):
	url = "http://thegamesdb.net/api/GetArt.php?id=" + online_game_id
	r = requests.get(url)
	game_tree = ET.fromstring(r.content)

	base_url = game_tree.find('baseImgUrl').text

	images = []

	for elem in game_tree.iter('Images'):
		for fanart_elem in elem.iter('fanart'):
			imageUrl = base_url + fanart_elem.find('original').text
			thumbUrl = base_url + fanart_elem.find('thumb').text
			description = "Fan Art"

			image = {'imageUrl': imageUrl, 'thumbUrl': thumbUrl, 'description': description}
			images.append(image)

		for boxart_elem in elem.iter('boxart'):
			imageUrl = base_url + boxart_elem.text
			thumbUrl = base_url + boxart_elem.get('thumb')
			description = "Box Art " + boxart_elem.get('side')

			image = {'imageUrl': imageUrl, 'thumbUrl': thumbUrl, 'description': description}
			images.append(image)

		for screenshot_elem in elem.iter('screenshot'):
			imageUrl = base_url + screenshot_elem.find('original').text
			thumbUrl = base_url + screenshot_elem.find('thumb').text
			description = "Screen Shot"

			image = {'imageUrl': imageUrl, 'thumbUrl': thumbUrl, 'description': description}
			images.append(image)

		for clearlogo_elem in elem.iter('clearlogo'):
			imageUrl = base_url + clearlogo_elem.text
			thumbUrl = base_url + clearlogo_elem.text
			description = "Clear Logo"

			image = {'imageUrl': imageUrl, 'thumbUrl': thumbUrl, 'description': description}
			images.append(image)

	return images