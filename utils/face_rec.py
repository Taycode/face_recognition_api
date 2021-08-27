"""Face Recognition Utils"""
import face_recognition as fr


def compare_faces(image_1, image_2):
	"""Compares faces and returns boolean"""

	first_image = fr.load_image_file(image_1)
	second_image = fr.load_image_file(image_2)

	first_image_enc = fr.face_encodings(first_image)
	second_image_enc = fr.face_encodings(second_image)

	if not len(first_image_enc) and len(second_image_enc):
		return False

	results = fr.compare_faces([first_image_enc], second_image_enc)
	return results[0]
