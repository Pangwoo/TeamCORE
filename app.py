import os
import zipfile
import uuid  # ✅ UUID 추가
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageOps

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "processed"
ZIP_FOLDER = "zips"  # ✅ ZIP 파일을 저장할 폴더 추가

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)  # ✅ ZIP 폴더 생성

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")

    if not files or files[0].filename == "":
        return "파일을 선택하세요.", 400

    idx = len(os.listdir(OUTPUT_FOLDER))  # 기존 파일 개수 확인
    for file in files:
        filename = file.filename
        unique_filename = f"{idx}_{filename}"
        idx += 1
        input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        output_path = os.path.join(OUTPUT_FOLDER, unique_filename)
        file.save(input_path)

        # ✅ 이미지 불러오기 및 반전
        image = Image.open(input_path).convert("L")
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            inverted_rgb = ImageOps.invert(Image.merge("RGB", (r, g, b)))
            inverted_image = Image.merge("RGBA", (*inverted_rgb.split(), a))
        else:
            inverted_image = ImageOps.invert(image)

        inverted_image.save(output_path)

    # ✅ ZIP 파일 이름을 UUID 기반으로 설정 (유니크하게)
    zip_uuid = uuid.uuid4().hex  # 32자리 랜덤 문자열
    zip_filename = os.path.join(ZIP_FOLDER, f"inverted_images_{zip_uuid}.zip")

    # ✅ ZIP 파일을 디스크에 저장
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(OUTPUT_FOLDER):
            file_path = os.path.join(OUTPUT_FOLDER, file)
            zipf.write(file_path, file)

    # ✅ 업로드 및 처리된 파일 삭제
    try:
        for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
            for file_name in os.listdir(folder):
                file_path = os.path.join(folder, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        print(f"파일 삭제 중 오류 발생: {e}")

    # ✅ 저장된 ZIP 파일 전송
    return send_file(zip_filename, mimetype="application/zip", as_attachment=True, download_name=f"inverted_images_{zip_uuid}.zip")

if __name__ == "__main__":
    app.run(debug=True)