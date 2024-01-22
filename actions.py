import os
from flask import Blueprint, request, redirect, url_for, jsonify, current_app
from helpers import get_secure_filename_filepath, download_from_s3
from PIL import Image

bp = Blueprint('actions', __name__, url_prefix='/actions')


@bp.route('/resize', methods=["POST"])
def resize():
    filename = request.json['filename']
    filename, filepath = get_secure_filename_filepath(filename)

    try:
        width, height = int(request.json['width']), int(request.json['height'])
        file_stream = download_from_s3(filename)
        image = Image.open(file_stream)
        out = image.resize((width, height))
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for('download_file', name=filename))

    except FileNotFoundError:
        return jsonify({'message': 'File not found'}), 404


@bp.route('/presets/<preset>', methods=["POST"])
def resize_preset(preset):
    presets = {'small': (640, 480), 'medium': (1280, 960), 'large': (1600, 1200)}

    if preset not in presets:
        return jsonify({'message': 'The preset is not available'}), 400

    filename = request.json['filename']
    filename, filepath = get_secure_filename_filepath(filename)

    try:
        size = presets[preset]
        image = Image.open(filepath)
        out = image.resize(size)
        out.save(filepath)
        return redirect(url_for('download_file', name=filename))

    except FileNotFoundError:
        return jsonify({'message': 'File not found'}), 404


@bp.route('/rotate', methods=["POST"])
def rotate():
    filename = request.json['filename']
    filename, filepath = get_secure_filename_filepath(filename)

    try:
        degree = float(request.json['degree'])
        image = Image.open(filepath)
        out = image.rotate(degree)
        out.save(filepath)
        return redirect(url_for('download_file', name=filename))

    except FileNotFoundError:
        return jsonify({'message': 'File not found'}), 404


@bp.route('/flip', methods=["POST"])
def flip():
    filename = request.json['filename']
    filename, filepath = get_secure_filename_filepath(filename)

    try:
        image = Image.open(filepath)
        out = None
        if request.json['direction'] == 'horizontal':
            out = image.transpose(Image.FLIP_TOP_BOTTOM)

        else:
            out = image.transpose(Image.FLIP_LEFT_RIGHT)
        out.save(filepath)
        return redirect(url_for('download_file', name=filename))

    except FileNotFoundError:
        return jsonify({'message': 'File not found'}), 404
