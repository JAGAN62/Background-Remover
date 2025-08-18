from flask import Flask, render_template, request
from rembg import remove
from PIL import Image
import io, base64
import os


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    image_data = None
    if request.method == "POST":
        file = request.files["image"]
        if file:
            input_image = Image.open(file.stream).convert("RGBA")
            output_image = remove(input_image)

            img_io = io.BytesIO()
            output_image.save(img_io, format="PNG")
            img_io.seek(0)

            # Encode image to base64
            image_data = base64.b64encode(img_io.getvalue()).decode("utf-8")

    return render_template("index.html", image_data=image_data)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render gives PORT env var
    app.run(host="0.0.0.0", port=port, debug=False)
