from flask import Flask, render_template, request
from rembg import remove
from PIL import Image
import io, base64, os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'Background-Remover-2025')

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file):
    """Validate uploaded file"""
    if not file:
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, "Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WEBP files."
    
    return True, "Valid file"

@app.route("/", methods=["GET", "POST"])
def index():
    image_data = None
    error_message = None
    
    if request.method == "POST":
        try:
            file = request.files.get("image")
            
            # Validate file
            is_valid, message = validate_image(file)
            if not is_valid:
                error_message = message
                return render_template("index.html", error_message=error_message)
            
            # Process image
            try:
                input_image = Image.open(file.stream)
                
                # Convert to RGBA if needed
                if input_image.mode != 'RGBA':
                    input_image = input_image.convert('RGBA')
                
                # Remove background
                output_image = remove(input_image)
                
                # Convert to base64
                img_io = io.BytesIO()
                output_image.save(img_io, format="PNG", optimize=True)
                img_io.seek(0)
                image_data = base64.b64encode(img_io.getvalue()).decode("utf-8")
                
                # Clean up
                input_image.close()
                output_image.close()
                
            except Exception as e:
                error_message = f"Error processing image: {str(e)}"
                
        except Exception as e:
            error_message = f"Upload error: {str(e)}"
    
    return render_template("index.html", image_data=image_data, error_message=error_message)

@app.errorhandler(413)
def too_large(e):
    return render_template("index.html", error_message="File too large"), 413

@app.errorhandler(500)
def internal_error(e):
    return render_template("index.html", error_message="Internal server error. Please try again."), 500

if __name__ == "__main__":
    # CRITICAL: Proper port binding for Render.com
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)