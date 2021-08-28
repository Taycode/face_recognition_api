"""Flask App"""
import os
from flask import Flask, request
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
from utils.face_rec import compare_faces
from utils.download_image import download_image
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
from bson import json_util
import json


load_dotenv()

cloudinary.config(
	cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
	api_key=os.getenv('CLOUDINARY_API_KEY'),
	api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

api = Api(title='Face Recognition API', description='Recognizes faces', doc='/docs/')
app = Flask(__name__)
api.init_app(app)

mongo_client = PyMongo(app, uri='mongodb://localhost:27017/face_rec')
db = mongo_client.db


def parse_json(data):
	"""Parses Json Data from mongo"""
	return json.loads(json_util.dumps(data))


@api.route('/hello')
class HelloWorld(Resource):
	"""Hello world"""
	def get(self):
		"""Get Hello World"""
		return {'hello': 'world'}


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
		uploaded_file = args['image']
		cloudinary_response = cloudinary.uploader.upload(uploaded_file)
		data = {
			'first_name': payload.get('first_name'),
			'matric_number': payload.get('matric_number'),
			'surname': payload.get('surname'),
			'image_url': cloudinary_response.get('url')
		}
		print(data)
		db.students.insert_one(data)
		return {'message': 'success'}, 201

	@staticmethod
	def get():
		"""Fetches students"""
		students = db.students.find()
		return parse_json(students), 200


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
		uploaded_file = args['image']
		data = {
			'surname': payload.get('surname'),
			'matric_number': payload.get('matric_number')
		}

		student = db.students.find_one(data)
		if not student:
			return {'message': 'Student not found'}

		student_image_url = student.get('image_url')
		student_image_file = download_image(student_image_url)
		matches = compare_faces(uploaded_file, student_image_file)
		os.remove(student_image_file)
		response = {'matches': bool(matches)}

		if bool(matches):
			response.update(parse_json(student))

		return response, 200


if __name__ == '__main__':
	app.run(debug=True)
