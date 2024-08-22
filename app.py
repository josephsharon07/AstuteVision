from flask import Flask, jsonify, request
import requests
import os
import cv2
import torch
from ultralytics import YOLO
import time
import math
from time import sleep

# Initialize the YOLO model
model = YOLO('best.pt')

app = Flask(__name__)

# Directory to save fetched images
FETCHED_IMAGES_FOLDER = 'fetched_images'
os.makedirs(FETCHED_IMAGES_FOLDER, exist_ok=True)

def extract_money_value(input_string):
    try:
        value = int(input_string.split()[1])
        return value
    except (IndexError, ValueError):
        return None

def predict(image_path):
    # Load the image with OpenCV
    image = cv2.imread(image_path)
    
    # Run the YOLO model on the image
    results = model(image)
    
    if results and len(results) > 0:
        try:
            box = results[0].boxes[0]
            label = results[0].names[int(box.cls)]
            label_value = extract_money_value(label)
            if label_value is not None:
                return label_value
        except (IndexError, AttributeError):
            pass
    
    return "-1"

def detect_uv(image_path):
    image = cv2.imread(image_path)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)

    # Noise reduction (important for better line detection)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    cv2.imwrite(" yes.jpg",opening)
    
    # Line detection using HoughLinesP (Probabilistic Hough Transform)

    
    lines = cv2.HoughLinesP(opening, 1, math.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    # Check if any lines were detected
    if lines is not None:
        return "True"  # Line detected, potentially real
    else:
        return "False"  # No line, potentially fake

    
@app.route('/predictions', methods=['GET'])
def home():
    try:
        en = requests.get('http://192.168.20.107:8080/enabletorch')
        sleep(1)
        foc = requests.get('http://192.168.20.107:8080/focus')
        # Fetch the image from the external source
        response = requests.get("http://192.168.20.107:8080/photo.jpg")
        response.raise_for_status()
        dis = requests.get('http://192.168.20.107:8080/disabletorch')
        
        # Save the fetched image to a local directory
        image_path = os.path.join(FETCHED_IMAGES_FOLDER, 'fetched_image.jpg')
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        # Run the prediction on the saved image
        prediction = predict(image_path)
        print(prediction)
        # Return the JSON response with the image path and prediction result
        return  str(prediction)
    
    except requests.RequestException as e:
        return "-1"

@app.route('/uv', methods=['GET'])
def uv():
    try:
        # Fetch the image from the external source
        response = requests.get("http://192.168.20.107:8080/photo.jpg")
        response.raise_for_status()
        
        # Save the fetched image to a local directory
        image_path = os.path.join(FETCHED_IMAGES_FOLDER, 'fetched_uv_image.jpg')
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        # Run the prediction on the saved image
        genuinity = detect_uv(image_path)
        
        # Return the JSON response with the image path and prediction result
        return str(genuinity)
    
    except requests.RequestException as e:
        return "-1"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
