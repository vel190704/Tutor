# backend/app/api/pdf.py
import os  #os-os interface to handle file paths and directories
import uuid #uuid-to create unique filenames while saving uploaded files
from datetime import datetime #to access current date and time
from flask import Blueprint, request, jsonify, current_app #blueprint-to create a blueprint for the PDF API, request-access uploaded file data and form responses, jsonify-to convert responses to JSON format, current_app-to access the current Flask application context
from werkzeug.utils import secure_filename #secure_filename-to ensure the filename is safe for saving on the filesystem
import PyPDF2 #PyPDF2-to read,validate and manipulate PDF files
from pdfminer.high_level import extract_text #pdfminer-to extract text content from PDF files
from io import BytesIO #BytesIO-to handle file-like objects in memory

pdf_bp = Blueprint('pdf', __name__) #Blueprint for the pdf 
ALLOWED_EXTENSIONS = {'pdf'} #Allowed file extensions for PDF uploads
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS #Check if the file has an allowed extension
def validate_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file) #Create a PDF reader object to validate the PDF file
        if len(reader.pages) == 0: #Check if the PDF has any pages
            current_app.logger.error("PDF file is empty or has no pages.")
            return False
        return True
    except Exception as e:
        current_app.logger.error(f"PDF validation error: {e}")
        return False

def get_pdf_metadata(file):  # Fixed function name typo
    try:
        reader = PyPDF2.PdfReader(file)
        metadata = reader.metadata
        return {
            'title': metadata.title if metadata.title else 'Unknown',
            'author': metadata.author if metadata.author else 'Unknown',
            'subject': metadata.subject if metadata.subject else 'Unknown',
            'created': metadata.created if metadata.created else 'Unknown'
        }
    except Exception as e:
        current_app.logger.error(f"Error extracting PDF metadata: {e}")
        return {}

@pdf_bp.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    filename = secure_filename(file.filename)
    file.seek(0)
    if not validate_pdf(file):  # Only validate once, after seek(0)
        return jsonify({'error': 'Invalid PDF file'}), 400

    max_size = 10 * 1024 * 1024  # 10MB
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > max_size:
        return jsonify({'error': 'File size exceeds limit of 10MB'}), 400

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')  # Fixed config access
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, f"{uuid.uuid4().hex}_{filename}")
    file.save(file_path)
    try:
        with open(file_path, 'rb') as f:
            meta_data = get_pdf_metadata(f)
            f.seek(0)
            text_content = extract_pdf_content(f)
            response_data = {
                'status': 'success',
                'filename': filename,
                'file_path': file_path,
                'metadata': meta_data,
                'content': text_content,
                'images': []
            }
            return jsonify(response_data), 201
    except Exception as e:
        current_app.logger.error(f"Error processing PDF file: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': 'Unexpected error occurred', 'details': str(e)}), 500
def extract_pdf_content(file):
    try:
        text = extract_text(file)
        return text if text else "No content found"
    except Exception as e:
        current_app.logger.error(f"Error extracting PDF content: {e}")
        return "Error extracting content"
@pdf_bp.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    if not validate_pdf(file):
        return jsonify({'error': 'Invalid PDF file'}), 400
    max_size = 10 * 1024 * 1024  # 10MB
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > max_size:
        return jsonify({'error': 'File size exceeds limit of 10MB'}), 400
    if not validate_pdf(file):
        return jsonify({'error': 'Invalid PDF file'}), 400
    file.seek(0)
    upload_folder= current_app.config['UPLOAD_FOLDER','uploads']
    os.makedirs(upload_folder, exist_ok=True)
    file_path=os.path.join(upload_folder, f"{uuid.uuid4().hex}_{filename}")
    file.save(file_path)
    try:
        with open(file_path, 'rb') as f:
            meta_data = get_pdf_metadata(f)
            f.seek(0)
            text_content = extract_pdf_content(f)
            f.seek(0)
            response_data={
                'status': 'success',
                'filename': filename,
                'file_path': file_path,
                'metadata': meta_data,
                'content': text_content,
                'images' : []
            }
            return jsonify(response_data), 201
    except Exception as e:
        current_app.logger.error(f"Error processing PDF file: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': 'Unexpected error occurred', 'details': str(e)}), 500 