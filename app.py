from flask import Flask, render_template, request, send_file
from PIL import Image, ImageOps
import os
import zipfile
import io
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")  # 여러 개의 파일 가져오기

    if not files or files[0].filename == "":
        return "파일을 선택하세요.", 400

    zip_buffer = io.BytesIO()  # ZIP 파일을 저장할 메모리 버퍼
    idx = 0
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            filename = file.filename
            unique_filename = f"{idx}_{filename}"
            idx = idx + 1
            input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            output_path = os.path.join(OUTPUT_FOLDER, unique_filename)
            file.save(input_path)

            # 이미지 불러오기 및 반전
            image = Image.open(input_path).convert("L")
            if image.mode == "RGBA":
                r, g, b, a = image.split()
                inverted_rgb = ImageOps.invert(Image.merge("RGB", (r, g, b)))
                inverted_image = Image.merge("RGBA", (*inverted_rgb.split(), a))
            else:
                inverted_image = ImageOps.invert(image)

            inverted_image.save(output_path)

            # ZIP 파일에 추가
            zipf.write(output_path, unique_filename)

    zip_buffer.seek(0)  # ZIP 파일 버퍼의 처음으로 이동
    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name="inverted_images.zip")

if __name__ == "__main__":
    app.run(debug=True)
