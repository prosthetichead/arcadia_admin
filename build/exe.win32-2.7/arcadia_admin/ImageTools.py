from PIL import Image



def is_jpg_progresive(image_path=None):
	if Image.open(image_path).info.get('progressive', '0') == 1:
		return True
	else:
		return False

def convert_to_jpg(image_path=None):
	image = Image.open(image_path)
	image.save(image_path, "JPEG",quality=75)