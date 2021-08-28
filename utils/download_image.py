"""Download image file"""

import requests
import shutil


def download_image(url):
	"""Download Image"""
	filename = url.split('/')[-1]
	response = requests.get(url, stream=True)
	response.raw.decode_content = True

	with open(filename, 'wb') as file:
		shutil.copyfileobj(response.raw, file)
	return filename
