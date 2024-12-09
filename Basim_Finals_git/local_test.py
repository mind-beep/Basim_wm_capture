from ultralytics import YOLO
from collections import Counter

# Load a model
model = YOLO("mark.pt")  # Load a custom model

# Predict with the model
results = model("checker.png")  # Predict on an image

# Access the first result
result = results[0]  # Extract the first (and only) Results object

# Access the boxes attribute
boxes = result.boxes  # Access the boxes attribute

if boxes is not None:
    # Extract class indices and confidence scores
    class_indices = boxes.cls.cpu().numpy()  # Convert class indices to NumPy array
    confidences = boxes.conf.cpu().numpy()   # Convert confidence scores to NumPy array

    # Filter objects with confidence >= 50%
    valid_detections = [
        int(cls) for cls, conf in zip(class_indices, confidences) if conf >= 0.5
    ]

    if valid_detections:
        # Count classes with valid detections
        class_names = result.names
        class_counts = Counter(valid_detections)

        # Print class counts
        print("Class Counts (Confidence >= 50%):")
        for class_index, count in class_counts.items():
            print(f"{class_names[class_index]}: {count}")
    else:
        print("No objects detected with confidence >= 50%.")
else:
    print("No detections found.")
