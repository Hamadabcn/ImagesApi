from flask import Flask, request, jsonify
from actions import bp as actionsbp
from helpers import allowed_extensions, get_secure_filename_filepath

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

app = Flask(__name__)

app.secret_key = 'SECRET_KEY'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

app.register_blueprint(actionsbp)


@app.route('/images', methods=['POST'])
def upload_images():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file was selected'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file was selected'}), 400

        if not allowed_extensions(file.filename):
            return jsonify({'error': 'The extension is not supported.'}), 400

        filename, filepath = get_secure_filename_filepath(file.filename)

        file.save(filepath)
        return jsonify({
            'message': 'File successfully uploaded',
            'filename': filename
        }), 201
