from flask import Flask, render_template, request, send_from_directory
import numpy as np
import tensorflow as tf
import uuid
import os

app = Flask(__name__)
# PATH SETUP
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "models", "plant_disease_recog_model_pwp.keras")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploadimages")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# LOAD MODEL
try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("✅ Model Loaded Successfully")
    print("Model Input Shape:", model.input_shape)
except Exception as e:
    print("❌ Error loading model:", e)
    model = None

# ✅ CORRECT 38 CLASS LABELS
plant_disease = [
'Apple___Apple_scab',
'Apple___Black_rot',
'Apple___Cedar_apple_rust',
'Apple___healthy',
'Blueberry___healthy',
'Cherry___Powdery_mildew',
'Cherry___healthy',
'Corn___Cercospora_leaf_spot Gray_leaf_spot',
'Corn___Common_rust',
'Corn___Northern_Leaf_Blight',
'Corn___healthy',
'Grape___Black_rot',
'Grape___Esca_(Black_Measles)',
'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
'Grape___healthy',
'Orange___Haunglongbing_(Citrus_greening)',
'Peach___Bacterial_spot',
'Peach___healthy',
'Pepper,_bell___Bacterial_spot',
'Pepper,_bell___healthy',
'Potato___Early_blight',
'Potato___Late_blight',
'Potato___healthy',
'Raspberry___healthy',
'Soybean___healthy',
'Squash___Powdery_mildew',
'Strawberry___Leaf_scorch',
'Strawberry___healthy',
'Tomato___Bacterial_spot',
'Tomato___Early_blight',
'Tomato___Late_blight',
'Tomato___Leaf_Mold',
'Tomato___Septoria_leaf_spot',
'Tomato___Spider_mites Two-spotted_spider_mite',
'Tomato___Target_Spot',
'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
'Tomato___Tomato_mosaic_virus',
'Tomato___healthy'
]

# DISEASE INFO
disease_info = {
"Potato___Early_blight": "Cause: Fungus. Treatment: Remove infected leaves and apply fungicide.",
"Potato___Late_blight": "Cause: Water mold. Treatment: Avoid moisture and use fungicide.",
"Tomato___Early_blight": "Treatment: Remove affected leaves, use fungicide spray.",
"Tomato___Late_blight": "Serious disease. Use copper-based fungicides immediately.",
"Tomato___healthy": "Your plant is healthy 🌿",
"Apple___Black_rot": "Remove infected parts and apply fungicide.",
"Corn___Common_rust": "Use resistant seeds and fungicide treatment."
}

# FORMAT LABEL (CLEAN TEXT)
def format_label(label):
    return label.replace("___", " - ").replace("_", " ")
# IMAGE PREPROCESSING
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

def extract_features(image_path):
    image = tf.keras.utils.load_img(image_path, target_size=(160, 160))
    image = tf.keras.utils.img_to_array(image)

    image = preprocess_input(image)  

    image = np.expand_dims(image, axis=0)

    return image

# PREDICTION FUNCTION
def model_predict(image_path):
    if model is None:
        return None, None, None

    img = extract_features(image_path)

    if img is None:
        return None, None, None

    prediction = model.predict(img, verbose=0)[0]

    print("Prediction shape:", prediction.shape)

    # Top 3 predictions
    top3_idx = prediction.argsort()[-3:][::-1]

    top3 = []
    for i in top3_idx:
        top3.append({
            "label": format_label(plant_disease[i]),
            "confidence": round(float(prediction[i]) * 100, 2)
        })

    predicted_label_raw = plant_disease[top3_idx[0]]
    predicted_label = format_label(predicted_label_raw)
    confidence = top3[0]["confidence"]

    return predicted_label, confidence, top3, predicted_label_raw

# -------------------------------
# ROUTES
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/contact/')
def contact():
    return render_template('contact.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# -------------------------------
# UPLOAD ROUTE
# -------------------------------
@app.route('/upload/', methods=['POST'])
def uploadimage():

    if 'img' not in request.files:
        return "No file uploaded"

    file = request.files['img']

    if file.filename == '':
        return "No file selected"

    filename = f"leaf_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    try:
        prediction, confidence, top3, raw_label = model_predict(filepath)

        if prediction is None:
            return "Prediction failed"

    except Exception as e:
        return f"Error processing image: {e}"

    # Get disease info
    info = disease_info.get(raw_label, "No detailed treatment available.")

    return render_template(
        'home.html',
        result=True,
        imagepath=f"/uploads/{filename}",
        prediction=prediction,
        confidence=confidence,
        top3=top3,
        info=info
    )

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)