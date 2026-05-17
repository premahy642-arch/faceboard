import os
# 1. SET THESE BEFORE TENSORFLOW LOADS
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

import tensorflow as tf
tf.config.set_visible_devices([], 'GPU') # Force CPU only

from flask import Flask, render_template, request
from deepface import DeepFace
import uuid
import cv2

app = Flask(__name__)

# Use absolute paths to avoid confusion in Docker/Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 2. WARM UP: This forces DeepFace to download models DURING build/startup
# so the app doesn't crash on the first user request.
try:
    print("Warming up DeepFace models...")
    DeepFace.build_model("VGG-Face")
    DeepFace.build_model("Age")
    DeepFace.build_model("Gender")
    DeepFace.build_model("Emotion")
except Exception as e:
    print(f"Preload warning: {e}")

@app.route('/', methods=['GET', 'POST'])
def home():
    result_data = None
    image_display_path = "" # Path for the HTML <img> tag

    if request.method == 'POST':
        image = request.files.get('image')

        if image and image.filename != "":
            filename = str(uuid.uuid4()) + ".jpg"
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(save_path)

            try:
                # Analyze Face
                analysis = DeepFace.analyze(
                    img_path=save_path,
                    actions=['age', 'gender', 'emotion'],
                    detector_backend='opencv',
                    enforce_detection=False
                )

                data = analysis[0]
                age = int(data['age'])
                gender = data['dominant_gender']
                emotion = data['dominant_emotion']

                # Logic for labels
                gender_label = "Man" if gender.lower() == "man" else "Woman"
                if age <= 17:
                    gender_label = "Boy" if gender.lower() == "man" else "Girl"

                # Age Group Logic
                if age <= 12: age_group = "Child"
                elif age <= 19: age_group = "Teenager"
                elif age <= 35: age_group = "Young Adult"
                elif age <= 55: age_group = "Adult"
                else: age_group = "Senior Citizen"

                # OpenCV Processing
                img = cv2.imread(save_path)
                
                # Colors: Age (Green), Gender (Blue), Emotion (Red)
                cv2.putText(img, f"Age: {age}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(img, f"Gender: {gender_label}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.putText(img, f"Emotion: {emotion}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                labeled_filename = "labeled_" + filename
                labeled_path = os.path.join(UPLOAD_FOLDER, labeled_filename)
                cv2.imwrite(labeled_path, img)

                result_data = {
                    "age": age,
                    "gender": gender_label,
                    "emotion": emotion,
                    "age_group": age_group
                }

                # This path needs to be relative for the <img> src in index.html
                image_display_path = f"static/uploads/{labeled_filename}"

            except Exception as e:
                result_data = {"error": f"Analysis failed: {str(e)}"}

    return render_template(
        'index.html',
        result=result_data,
        image_path=image_display_path
    )

if __name__ == '__main__':
    # Threaded=False is often safer for memory-heavy AI apps on low-tier servers
    app.run(host="0.0.0.0", port=5000, threaded=False)