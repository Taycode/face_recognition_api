"""Face Recognition Utils"""
import face_recognition as fr


def compare_faces(image_1, image_others):
	"""Compares faces and returns boolean"""

	first_image = fr.load_image_file(image_1)
	other_images = list(map(fr.load_image_file, image_others))

	first_image_enc = fr.face_encodings(first_image)
	other_images_enc = list(map(fr.face_encodings, other_images))
	if not (first_image_enc and other_images_enc):
		return False

	first_image_enc = first_image_enc[0]
	other_images_enc = list(map(lambda x: x[0], other_images_enc))

	results = fr.compare_faces(other_images_enc, first_image_enc, 1.0)
	return results[0]


def image_isvalid(image):
	"""Checks image validity"""
	loaded_image = fr.load_image_file(image)
	image_encoding = fr.face_encodings(loaded_image)
	return bool(image_encoding)
