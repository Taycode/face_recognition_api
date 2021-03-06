"""Flask App"""
import os

import PIL.Image
from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api, Resource
from werkzeug.datastructures import FileStorage
from utils.face_rec import compare_faces, image_isvalid
from utils.download_image import download_image
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
from bson import json_util
import json


load_dotenv()

# Configure Cloudinary
cloudinary.config(
	cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
	api_key=os.getenv('CLOUDINARY_API_KEY'),
	api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Initialize Flask App
api = Api(title='Face Recognition API', description='Recognizes faces', doc='/docs/')
app = Flask(__name__)
api.init_app(app)
CORS(app)

# Connect to MongoDB
mongo_client = PyMongo(app, uri=os.getenv('MONGO_URI'))
db = mongo_client.db


def parse_json(data):
	"""Parses Json Data from mongo"""
	return json.loads(json_util.dumps(data))


create_student_parser = api.parser()
create_student_parser.add_argument('image', location='files', type=FileStorage, required=True)
create_student_parser.add_argument('first_name', location='form')
create_student_parser.add_argument('matric_number', location='form')
create_student_parser.add_argument('surname', location='form')


@api.route('/students')
class CreateStudent(Resource):
	"""Create Student Resource"""

	@staticmethod
	@api.expect(create_student_parser)
	def post():
		"""Creates Student"""
		args = create_student_parser.parse_args()
		payload = request.form

		# Upload Image to Cloudinary
		# Save Cloudinary Image Url to DB
		uploaded_file = args['image']

		cloudinary_response = cloudinary.uploader.upload(uploaded_file)

		if not image_isvalid(uploaded_file):
			return {'message': 'Image is not good enough, can not identify face'}, 400

		# Create Student Data
		data = {
			'first_name': payload.get('first_name'),
			'matric_number': payload.get('matric_number'),
			'surname': payload.get('surname'),
			'image_url': [cloudinary_response.get('url')]
		}
		db.students.insert_one(data)
		return {'message': 'success'}, 201

	@staticmethod
	def get():
		"""Fetches students"""
		students = db.students.find()
		return parse_json(students), 200


add_image_parser = api.parser()
add_image_parser.add_argument('image', location='files', type=FileStorage, required=True)
add_image_parser.add_argument('matric_number', location='form')


@api.route('/student/update')
class AddImageForStudent(Resource):
	"""Adds Image to Student profile"""

	@staticmethod
	@api.expect(add_image_parser)
	def patch():
		"""Adds Image"""
		args = add_image_parser.parse_args()
		payload = request.form
		matric_number = payload.get('matric_number')
		student = db.students.find_one({
			'matric_number': matric_number
		})
		if not student:
			return {'message': 'Student not found'}, 404

		uploaded_image = args['image']

		cloudinary_response = cloudinary.uploader.upload(uploaded_image)

		if not image_isvalid(uploaded_image):
			return {'message': 'Image is not good enough, can not identify face'}, 400

		db.students.update_one(
			{'matric_number': matric_number},
			{'$push': {'image_url': cloudinary_response.get('url')}}
		)
		return {'message': 'success'}, 200


compare_parser = api.parser()
compare_parser.add_argument('matric_number', location='form')
compare_parser.add_argument('surname', location='form')
compare_parser.add_argument('image', location='files', type=FileStorage, required=True)


@api.route('/compare')
class CompareFaces(Resource):
	"""Compare Faces Resource"""
	@staticmethod
	@api.expect(compare_parser)
	def post():
		"""Compares faces"""
		args = compare_parser.parse_args()
		payload = request.form

		# Fetch Student by details
		data = {
			'surname': payload.get('surname'),
			'matric_number': payload.get('matric_number')
		}

		student = db.students.find_one(data)
		if not student:
			return {'message': 'Student not found'}

		# Download Student Image

		student_image_url = student.get('image_url')
		student_image_files = list(map(download_image, student_image_url))

		# Compare uploaded image to student image
		uploaded_file = args['image']

		if not image_isvalid(uploaded_file):
			return {'message': 'Image is not good enough, can not identify face'}, 400

		matches = compare_faces(uploaded_file, student_image_files)

		# Delete Downloaded Image to free up space
		for _ in student_image_files:
			os.remove(_)

		response = {'matches': bool(matches)}

		# If Face matches, add student data to response
		if bool(matches):
			response.update(parse_json(student))

		return response, 200


if __name__ == '__main__':
	app.run(debug=True)
