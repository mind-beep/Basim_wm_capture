from flask import Flask, request, jsonify
from ultralytics import YOLO
from collections import Counter
import cv2
import os

# Initialize Flask app
app = Flask(__name__)

# Load the YOLO model once
model = YOLO("mark.pt")  # Replace "mark.pt" with your model's path

@app.route('/detect', methods=['POST'])
def detect_objects():
    # Check if an image is uploaded
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400

    image_file = request.files['image']

    # Save the image to a temporary location
    image_path = "temp_image.jpg"
    image_file.save(image_path)

    try:
        # Predict with YOLO model
        results = model(image_path)
        result = results[0]  # Extract the first Results object

        # Process the boxes
        boxes = result.boxes
        if boxes is not None:
            # Extract class indices and confidence scores
            class_indices = boxes.cls.cpu().numpy()
            confidences = boxes.conf.cpu().numpy()

            # Filter classes with confidence >= 50%
            valid_detections = [
                (int(cls), float(conf))  # Convert to standard Python types
                for cls, conf in zip(class_indices, confidences) if conf >= 0.5
            ]

            # Count classes
            class_names = result.names
            filtered_counts = Counter([cls for cls, _ in valid_detections])

            # Prepare the response
            response = {
                "class_counts": {class_names[cls]: count for cls, count in filtered_counts.items()},
                #"confidences": [
                #    {"class": class_names[cls], "confidence": round(conf, 2)}
                #    for cls, conf in valid_detections
                #]
            }
        else:
            response = {"class_counts": {}}

        return jsonify(response)

    finally:
        # Clean up the temporary image
        if os.path.exists(image_path):
            os.remove(image_path)


@app.route('/process_video', methods=['POST'])
def process_video():
    # Check if a video file is uploaded
    if 'video' not in request.files:
        return jsonify({'error': 'No video file uploaded'}), 400

    video_file = request.files['video']
    video_path = "temp_video.mp4"
    video_file.save(video_path)

    try:
        cap = cv2.VideoCapture(video_path)
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))  # Get the frame rate of the video
        frame_count = 0
        all_detections = []

        if not cap.isOpened():
            return jsonify({'error': 'Failed to process video file'}), 500

        # Process video frames
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_rate == 0:  # Extract 1 frame per second
                results = model(frame)
                result = results[0]  # Extract the first Results object
                boxes = result.boxes

                if boxes is not None:
                    # Extract class indices and confidence scores
                    class_indices = boxes.cls.cpu().numpy()
                    confidences = boxes.conf.cpu().numpy()

                    # Filter classes with confidence >= 50%
                    valid_detections = [
                        (int(cls), float(conf))  # Convert to standard Python types
                        for cls, conf in zip(class_indices, confidences) if conf >= 0.5
                    ]
                    all_detections.extend(valid_detections)

            frame_count += 1

        cap.release()

        # Aggregate results
        if all_detections:
            class_names = model.names
            class_counts = Counter([cls for cls, _ in all_detections])

            response = {
                "class_counts": {class_names[cls]: count for cls, count in class_counts.items()},
                #"confidences": [
                #    {"class": class_names[cls], "confidence": round(conf, 2)}
                #    for cls, conf in all_detections
                #]
            }
        else:
            response = {"message": "No objects detected with confidence >= 50%."}

        return jsonify(response)

    finally:
        # Clean up the temporary video
        if os.path.exists(video_path):
            os.remove(video_path)


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001)
