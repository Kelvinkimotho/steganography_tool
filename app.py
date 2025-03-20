from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import os
from werkzeug.utils import secure_filename
from utils.stego import hide_message, extract_message
from utils.encryptor import encrypt_message, decrypt_message

app = Flask(__name__)
app.secret_key = "supersecretkey"  # I'll change this in production

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

# Allowed file types: PNG, JPG, BMP (expandable)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "image" not in request.files or "message" not in request.form:
            flash("Missing file or message!", "danger")
            return redirect(url_for("index"))

        file = request.files["image"]
        message = request.form["message"]
        password = request.form.get("password")

        if file.filename == "":
            flash("No file selected!", "danger")
            return redirect(url_for("index"))

        if not allowed_file(file.filename):
            flash("Invalid file type! Please upload a PNG, JPG, or BMP image.", "danger")
            return redirect(url_for("index"))

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Encrypt message if password is provided
        if password:
            message = encrypt_message(message, password)

        # Hide message in image
        output_filename = f"stego_{filename}"
        output_path = os.path.join(app.config["PROCESSED_FOLDER"], output_filename)
        hide_message(filepath, message, output_path)

        # Store encoded file path in session
        session["last_encoded"] = output_filename

        flash("Message hidden successfully! You can now download it.", "success")
        return redirect(url_for("index"))

    encoded_file = session.get("last_encoded")
    return render_template("index.html", encoded_file=encoded_file)

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(app.config["PROCESSED_FOLDER"], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("File not found!", "danger")
        return redirect(url_for("index"))

@app.route("/decode", methods=["GET", "POST"])
def decode():
    if request.method == "POST":
        if "image" not in request.files:
            flash("No file uploaded!", "danger")
            return redirect(url_for("decode"))

        file = request.files["image"]
        password = request.form.get("password")

        if file.filename == "":
            flash("No file selected!", "danger")
            return redirect(url_for("decode"))

        if not allowed_file(file.filename):
            flash("Invalid file type! Please upload a PNG, JPG, or BMP image.", "danger")
            return redirect(url_for("decode"))

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Extract message
        hidden_message = extract_message(filepath)

        # Decrypt message if password is provided
        if password:
            try:
                hidden_message = decrypt_message(hidden_message, password)
            except Exception:
                flash("Incorrect password or corrupted message!", "danger")
                return redirect(url_for("decode"))

        flash(f"Extracted Message: {hidden_message}", "success")

    return render_template("decode.html")


if __name__ == "__main__":
    app.run(debug=True)
