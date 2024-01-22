from datetime import datetime
import os
import shutil
from flask import Blueprint, request, redirect, current_app, url_for
from helpers import get_secure_filename_filepath, download_from_s3
from PIL import Image
from zipfile import ZipFile

bp = Blueprint('android', __name__, url_prefix='/android')

ICON_SIZE = (29, 40, 57, 58, 60, 80, 87, 114, 120, 180, 1024)


@bp.route('/', methods=["POST"])
def create_images():
    filename = request.json['filename']
    filename, filepath = get_secure_filename_filepath(filename)

    tempfolder = os.path.join(current_app.config['DOWNLOAD_FOLDER'], 'temp')

    # Check if the directory already exists
    if not os.path.exists(tempfolder):
        try:
            # Create the directory if it doesn't exist
            os.makedirs(tempfolder)
            print(f"Directory '{tempfolder}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{tempfolder}': {e}")
            # Handle the error, log, or raise an exception as needed
            return f"Error creating directory '{tempfolder}': {e}"

    try:
        for size in ICON_SIZE:
            outfile = os.path.join(tempfolder, f'{size}.png')
            # image = Image.open(filepath)
            file_stream = download_from_s3(filename)
            image = Image.open(file_stream)
            out = image.resize((size, size))
            out.save(outfile, 'PNG')
    except Exception as e:
        print(f"Error processing image: {e}")
        # Handle the error, log, or raise an exception as needed
        return f"Error processing image: {e}"

    now = datetime.now()
    timestamp = str(datetime.timestamp(now)).rsplit('.')[0]
    zipfilename = f'{timestamp}.zip'
    zipfilepath = os.path.join(current_app.config['DOWNLOAD_FOLDER'], zipfilename)

    with ZipFile(zipfilepath, 'w') as zipObj:
        for foldername, subfolders, filenames in os.walk(tempfolder):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                zipObj.write(filepath, os.path.basename(filepath))

    # Clean up the temporary folder
    shutil.rmtree(tempfolder)

    return redirect(url_for('download_file', name=zipfilename))
