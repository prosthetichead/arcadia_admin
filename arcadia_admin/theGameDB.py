__author__ = 'Ashley'
import requests
import xml.etree.ElementTree as ET

gameDB_platform_choices = {0: "None Chosen"}

def get_platforms():
	r = requests.get('http://thegamesdb.net/api/GetPlatformsList.php')
	platforms_tree = ET.fromstring(r.content)
	# platforms_root = platformsTree.getroot()

	gameDB_platforms = []
	for elem in platforms_tree.iter('Platform'):
		pf_id = elem.find('id').text
		pf_name = elem.find('name').text
		if elem.find('alias') is not None:
			pf_alias = elem.find('alias').text
		else:
			pf_alias = elem.find('name').text

		gameDB_platforms.append({"id": pf_id, "name": pf_name, "alias": pf_alias})
	return gameDB_platforms


def refresh_platform_choices():
	r = requests.get('http://thegamesdb.net/api/GetPlatformsList.php')
	platforms_tree = ET.fromstring(r.content)

	gameDB_platform_choices.clear()
	gameDB_platform_choices.update({0: "None Chosen"})
	for elem in platforms_tree.iter('Platform'):
		pf_id = elem.find('id').text
		pf_name = elem.find('name').text
		gameDB_platform_choices.update({pf_id: pf_name})
	print "gameDB platform choice refresh complete"