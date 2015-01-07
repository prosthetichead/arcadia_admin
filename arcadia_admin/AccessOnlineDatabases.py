__author__ = 'Ashley'
import requests
import xml.etree.ElementTree as ET

thegamesdb_platform_choices = {0: "None Chosen"}
giantbomb_platform_choices = {0: "None Chosen"}

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
