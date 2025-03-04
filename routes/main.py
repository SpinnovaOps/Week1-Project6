import os
import re
import mimetypes
import google.generativeai as genai
from flask import Blueprint, render_template, request, redirect, url_for, flash, g

# Initialize Blueprint
main_bp = Blueprint('main', __name__)

# Configure Google Generative AI
GOOGLE_API_KEY = "API_Key"
genai.configure(api_key=GOOGLE_API_KEY)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Regex Pattern for Allowed Filenames (only alphanumeric, underscore, dot)
FILENAME_REGEX = r'^[\w,\s-]+\.[A-Za-z]{1,5}$'

# 🟢 Before Request Hook
@main_bp.before_request
def before_request_func():
    g.request_info = f"Processing {request.path}"
    print(g.request_info)  # Logs every request

# 🔴 After Request Hook
@main_bp.after_request
def after_request_func(response):
    response.headers["X-Processed-By"] = "Flask-Blueprint-System"
    return response

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('main.index'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('main.index'))

    # ✅ Validate filename with Regex
    if not re.match(FILENAME_REGEX, file.filename):
        flash('Invalid filename! Only alphanumeric, underscores, spaces, and dots are allowed.')
        return redirect(url_for('main.index'))

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Detect file type
    mime_type, _ = mimetypes.guess_type(file.filename)

    if mime_type and mime_type.startswith("text"):
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            content = "Unable to decode file as UTF-8 text."
    else:
        content = f"This file appears to be binary (e.g., {mime_type or 'unknown type'}), and cannot be displayed."

    return render_template('display.html', filename=file.filename, content=content)

@main_bp.route('/summarize/<filename>')
def summarize(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # ✅ Validate filename with Regex
    if not re.match(FILENAME_REGEX, filename):
        flash('Invalid filename!')
        return redirect(url_for('main.index'))

    # Read the file content
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        flash("Cannot summarize this file as it is not a readable text format.")
        return redirect(url_for('main.index'))

    # Use Gemini-Pro to generate a summary
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Summarize this document: {content}")

    summary = response.text if response and hasattr(response, 'text') else "Failed to generate summary."

    return render_template('summary.html', filename=filename, summary=summary)


