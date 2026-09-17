# GeoX6 - AI-Based Rockfall Prediction System 
 
## Overview 
 
GeoX6 is an AI and IoT based rockfall risk prediction system designed to monitor slope conditions and classify rockfall risk into: 
 
- LOW 
- MEDIUM 
- HIGH 
 
The system collects environmental and slope-related sensor data and sends it to a Random Forest machine learning model for risk prediction. 
 
## System Architecture 
 
Sensors 
↓ 
ESP32 / Wokwi 
↓ 
Wi-Fi 
↓ 
Flask API 
↓ 
Random Forest Model 
↓ 
Risk Prediction 
↓ 
OLED Display + LEDs + Buzzer 
 
## Sensors 
 
The prototype uses: 
 
- Rainfall sensor 
- Soil moisture sensor 
- Vibration sensor 
- Slope displacement sensor 
- MPU6050 tilt sensor 
 
## Machine Learning 
 
### Algorithm 
 
Random Forest Classifier 
 
### Input Features 
 
1. Rainfall 
2. Soil Moisture 
3. Vibration 
4. Slope Displacement 
 
### Output 
 
- Risk Level 
- Risk Probability 
 
## Dataset 
 
The initial model was developed using a synthetic prototype dataset containing 1,200 samples. 
 
The dataset contains three risk classes: 
 
- LOW 
- MEDIUM 
- HIGH 
 
Due to limited availability of site-specific labeled rockfall data, a synthetic dataset was used for initial model prototyping. The system is designed to be retrained with real-time sensor data during field deployment. 
 
## Model Performance 
 
The Random Forest model achieved: 
 
**90.42% test accuracy** 
 
This result is based on the synthetic prototype test dataset and should not be interpreted as real-world field accuracy. 
 
## Technologies Used 
 
### Programming 
- Python 
- MicroPython 
 
### Machine Learning 
- Scikit-learn 
- Random Forest 
 
### Data Processing 
- Pandas 
- NumPy 
 
### IoT 
- ESP32 
- Wokwi 
 
### API 
- Flask 
 
### Communication 
- Wi-Fi 
- HTTP/REST API 
 
## Project Files 
 
- `app.py` - Flask API server 
- `rockfall_random_forest_model.pkl` - trained Random Forest model 
- `rockfall_prediction_synthetic_dataset_balanced.csv` - prototype dataset 
- `main.py` - ESP32 MicroPython code 
- `diagram.json` - Wokwi circuit configuration 
- `requirements.txt` - Python dependencies 
 
## 🎥 Demo Video

[Watch the GeoX6 Demo Video](https://drive.google.com/file/d/167zKE1EJvtSkbObxhL9FfyYfoH67PoA9/view?usp=drive_link)

## Running the AI Server 
 
Install dependencies: 
 
```bash
pip install -r requirements.txt