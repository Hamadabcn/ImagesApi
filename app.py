from flask import Flask, request, jsonify, send_from_directory
from actions import bp as actionsbp
from android import bp as androidbp
from filters import bp as filtersbp
from helpers import allowed_extensions, get_secure_filename_filepath, upload_to_s3
import boto3, botocore


UPLOAD_FOLDER = 'uploads/'
DOWNLOAD_FOLDER = 'downloads/'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

app = Flask(__name__)

app.secret_key = 'SECRET_KEY'

app.config['S3_BUCKET'] = 'image-api-bucket-2024'
app.config['S3_KEY'] = 'Your Secret Key'
app.config['S3_SECRET'] = 'Your Secret Key'
app.config['S3_LOCATION'] = 'https://image-api-bucket-2024.s3.eu-west-3.amazonaws.com/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

app.register_blueprint(actionsbp)
app.register_blueprint(filtersbp)
app.register_blueprint(androidbp)


@app.route('/')
def index():
    return jsonify({'message': 'Welcome to Image API'})


@app.route('/images', methods=['GET', 'POST'])
def images():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file was selected'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file was selected'}), 400

        if not allowed_extensions(file.filename):
            return jsonify({'error': 'The extension is not supported.'}), 400

        # filename, filepath = get_secure_filename_filepath(file.filename)

        output = upload_to_s3(file, app.config['S3_BUCKET'])
        # file.save(filepath)
        return jsonify({
            'message': 'File successfully uploaded',
            'filename': output
        }), 201

    images = []
    s3_resources = boto3.resource('s3', aws_access_key_id=app.config['S3_KEY'],
                                  aws_secret_access_key=app.config['S3_SECRET'])
    s3_bucket = s3_resources.Bucket(app.config['S3_BUCKET'])
    for obj in s3_bucket.objects.filter(Prefix='uploads/'):
        if obj.key == 'uploads/':
            continue
        images.append(obj.key)

    return jsonify({'data': images}), 200


@app.route('/downloads/<name>')
def download_file(name):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], name)
