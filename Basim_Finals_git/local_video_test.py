from ultralytics import YOLO
from collections import Counter
import cv2
import os

# Load the YOLO model
model = YOLO("mark.pt")  # Load your custom model


def process_frame(image, model):
    """
    Process a single frame using the YOLO model.
    Args:
        image: Frame to process.
        model: Preloaded YOLO model.

    Returns:
        List of tuples containing class index and confidence for detections with confidence >= 50%.
    """
    results = model(image)
    result = results[0]  # Extract the first (and only) Results object
    boxes = result.boxes  # Access the boxes attribute

    if boxes is not None:
        class_indices = boxes.cls.cpu().numpy()
        confidences = boxes.conf.cpu().numpy()

        # Filter objects with confidence >= 50%
        valid_detections = [
            (int(cls), float(conf))
            for cls, conf in zip(class_indices, confidences) if conf >= 0.5
        ]
        return valid_detections
    else:
        return []


def process_video(video_path, model):
    """
    Process a video file, extract 1 frame per second, and return aggregated detection results.
    Args:
        video_path: Path to the video file.
        model: Preloaded YOLO model.

    Returns:
        Dictionary of aggregated class counts and confidences.
    """
    cap = cv2.VideoCapture(video_path)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))  # Get the frame rate of the video
    frame_count = 0
    all_detections = []

    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return {"message": "Failed to process video."}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_rate == 0:  # Extract 1 frame per second
            detections = process_frame(frame, model)
            all_detections.extend(detections)  # Collect all detections

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

    if all_detections:
        # Aggregate results
        class_counts = Counter([cls for cls, _ in all_detections])
        confidences = [(cls, conf) for cls, conf in all_detections]

        # Get class names
        result_names = model.names

        # Format output
        return {
            "class_counts": {result_names[cls]: count for cls, count in class_counts.items()},
            "confidences": [
                {"class": result_names[cls], "confidence": round(conf, 2)}
                for cls, conf in confidences
            ]
        }
    else:
        return {"message": "No objects detected with confidence >= 50%."}


# Example Usage
if __name__ == "__main__":
    video_file = "test.mp4"  # Replace with your video file path
    output = process_video(video_file, model)

    # Print the results
    print("Video Detection Results:")
    print(output)
