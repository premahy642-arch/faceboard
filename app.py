from flask import Flask, render_template, request
from deepface import DeepFace
import os
import uuid
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def home():

    result_data = None
    image_path = ""

    if request.method == 'POST':

        image = request.files['image']

        if image.filename != "":

            filename = str(uuid.uuid4()) + ".jpg"

            image_path = os.path.join(UPLOAD_FOLDER, filename)

            image.save(image_path)

            try:

                # Analyze Face
                analysis = DeepFace.analyze(
                    img_path=image_path,
                    actions=['age', 'gender', 'emotion'],
                    detector_backend='opencv',
                    enforce_detection=False
                )

                data = analysis[0]

                age = int(data['age'])
                gender = data['dominant_gender']
                emotion = data['dominant_emotion']

                # Gender Labels
                if gender.lower() == "man":

                    if age <= 17:
                        gender_label = "Boy"
                    else:
                        gender_label = "Man"

                else:

                    if age <= 17:
                        gender_label = "Girl"
                    else:
                        gender_label = "Woman"

                # Age Group
                if age <= 12:
                    age_group = "Child"

                elif age <= 19:
                    age_group = "Teenager"

                elif age <= 35:
                    age_group = "Young Adult"

                elif age <= 55:
                    age_group = "Adult"

                else:
                    age_group = "Senior Citizen"

                # Load image using OpenCV
                img = cv2.imread(image_path)

                # Labels
                label1 = f"Age : {age}"
                label2 = f"Gender : {gender_label}"
                label3 = f"Emotion : {emotion}"

                # Draw Labels
                cv2.putText(
                    img,
                    label1,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    img,
                    label2,
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 0, 0),
                    2
                )

                cv2.putText(
                    img,
                    label3,
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

                # Save labeled image
                labeled_filename = "labeled_" + filename

                labeled_path = os.path.join(
                    UPLOAD_FOLDER,
                    labeled_filename
                )

                cv2.imwrite(labeled_path, img)

                result_data = {
                    "age": age,
                    "gender": gender_label,
                    "emotion": emotion,
                    "age_group": age_group
                }

                image_path = labeled_path

            except Exception as e:

                result_data = {
                    "error": str(e)
                }

    return render_template(
        'index.html',
        result=result_data,
        image_path=image_path
    )

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=5000)