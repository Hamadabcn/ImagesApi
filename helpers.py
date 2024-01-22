import os
import boto3
from botocore.exceptions import ClientError
from flask import current_app, jsonify
from werkzeug.utils import secure_filename


def allowed_extensions(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def get_secure_filename_filepath(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    return filename, filepath


def upload_to_s3(file, bucket_name, acl='public-read'):
    s3_client = boto3.client('s3', aws_access_key_id=current_app.config['S3_KEY'],
                             aws_secret_access_key=current_app.config['S3_SECRET'])
    file.filename = secure_filename(file.filename)
    file.filename = os.path.join('uploads/', file.filename)

    try:
        s3_client.upload_fileobj(file, bucket_name, file.filename,
                                 ExtraArgs={'ACL': acl, 'ContentType': file.content_type})

    except ClientError as e:
        return jsonify({'message': 'Cannot upload files to S3 account'}), 400

    return file.filename


def download_from_s3(filename):
    if not os.path.exists(current_app.config['DOWNLOAD_FOLDER']):
        os.makedirs(current_app.config['DOWNLOAD_FOLDER'])

    s3_object_path = os.path.join('uploads/', filename)
    s3_resource = boto3.resource('s3', aws_access_key_id=current_app.config['S3_KEY'],
                                 aws_secret_access_key=current_app.config['S3_SECRET'])
    bucket = s3_resource.Bucket(current_app.config['S3_BUCKET'])
    s3_object = bucket.Object(s3_object_path)
    response = s3_object.get()
    return response['Body']
