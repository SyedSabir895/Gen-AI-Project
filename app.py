import os
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from PIL import Image
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './images'  # Temporary storage for uploaded images
app.config['DOWNLOAD_FOLDER'] = './static/downloads'  # Storage for converted PDFs
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size: 16 MB
app.secret_key = 'supersecretkey'  # Secret key for flashing messages
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit


# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if uploaded file is an allowed image type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the upload page."""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_image_to_pdf():
    """Handle image upload and conversion to PDF."""
    if 'file' not in request.files:
        flash('No file part in the request.')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file.')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # Save the uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        try:
            # Convert image to PDF
            output_filename = f"{os.path.splitext(filename)[0]}.pdf"
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)

            image = Image.open(input_path)
            image_converted = image.convert('RGB')
            image_converted.save(output_path)

            # Clean up uploaded image
            os.remove(input_path)

            # Provide the converted PDF as a downloadable file
            return send_file(output_path, as_attachment=True)

        except Exception as e:
            flash(f"Error during conversion: {e}")
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload a PNG, JPG, or JPEG file.')
        return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)

