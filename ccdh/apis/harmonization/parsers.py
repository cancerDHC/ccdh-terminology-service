# parsers.py
import werkzeug
from flask_restx import reqparse

file_upload = reqparse.RequestParser()
file_upload.add_argument('tsv_file',
                         type=werkzeug.datastructures.FileStorage,
                         location='files',
                         required=True,
                         help='TSV file')
