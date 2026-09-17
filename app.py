from flask import Flask, request, jsonify
import joblib
import pandas as pd

# Load the trained Random Forest model
model = joblib.load("rockfall_random_forest_model.pkl")

app = Flask(__name__)


@app.route("/")
def home():
    return "Rockfall AI Server is Running!"


@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    # Create input for the Random Forest model
    X = pd.DataFrame({
        "Rainfall_mm": [float(data["rainfall"])],
        "Soil_Moisture_percent": [float(data["moisture"])],
        "Vibration_g": [float(data["vibration"])],
        "Slope_Displacement_mm": [float(data["displacement"])]
    })

    # Predict risk
    prediction = model.predict(X)[0]

    # Get probability
    probabilities = model.predict_proba(X)[0]

    probability = probabilities[
        list(model.classes_).index(prediction)
    ] * 100

    print("-----------------------------------")
    print("Sensor Data Received")
    print("Rainfall:", data["rainfall"], "mm")
    print("Moisture:", data["moisture"], "%")
    print("Vibration:", data["vibration"], "g")
    print("Displacement:", data["displacement"], "mm")
    print("Risk:", prediction)
    print("Probability:", round(probability, 2), "%")
    print("-----------------------------------")

    return jsonify({
        "risk": prediction,
        "probability": round(float(probability), 2)
    })


app.run(host="0.0.0.0", port=5000)