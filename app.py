"""Flask App"""

from flask import Flask
from flask_restx import Api, Resource
from werkzeug.datastructures import FileStorage
from utils.face_rec import compare_faces


api = Api(title='Face Recognition API', description='Recognizes faces', doc='/docs/')
app = Flask(__name__)
api.init_app(app)


upload_parser = api.parser()
upload_parser.add_argument('image', location='files', type=FileStorage, required=True)


@api.route('/hello')
class HelloWorld(Resource):
	"""Hello world"""
	def get(self):
		"""Get Hello World"""
		return {'hello': 'world'}


@api.route('/upload/')
@api.expect(upload_parser)
class Upload(Resource):
	"""Upload Resource"""
	def post(self):
		"""Collects file"""
		args = upload_parser.parse_args()
		uploaded_file = args['image']
		matches = compare_faces('images/myself2.jpeg', uploaded_file)
		return {'matches': bool(matches)}, 200


if __name__ == '__main__':
	app.run(debug=True)
