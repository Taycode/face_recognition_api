"""Face Recognition Utils"""
import face_recognition as fr


def compare_faces(image_1, image_2):
	"""Compares faces and returns boolean"""

	first_image = fr.load_image_file(image_1)
	second_image = fr.load_image_file(image_2)

	first_image_enc = fr.face_encodings(first_image)
	second_image_enc = fr.face_encodings(second_image)

	if not (first_image_enc and second_image_enc):
		return False

	first_image_enc = first_image_enc[0]
	second_image_enc = second_image_enc[0]

	results = fr.compare_faces([first_image_enc], second_image_enc)
	return results[0]
