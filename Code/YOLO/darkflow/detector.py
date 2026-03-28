from ultralytics import YOLO
import cv2
import os

class VehicleDetector:
    def __init__(self, model_name='yolov8n.pt'):
        # This will download the weights automatically on first run
        self.model = YOLO(model_name)
        # Class mapping for COCO: 2: car, 3: motorcycle, 5: bus, 7: truck
        self.target_classes = [2, 3, 5, 7]
        self.class_names = {2: 'car', 3: 'bike', 5: 'bus', 7: 'truck'}

    def detect_and_count(self, image_path):
        """
        Input: Path to a lane image
        Output: Dictionary of counts: {'car': 3, 'bus': 1, ...}
        """
        if not os.path.exists(image_path):
            return {'car':0, 'bus':0, 'truck':0, 'bike':0}
            
        results = self.model(image_path, conf=0.25, verbose=False)
        counts = {'car': 0, 'bus': 0, 'truck': 0, 'bike': 0, 'total': 0}
        
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                if cls_id in self.target_classes:
                    label = self.class_names[cls_id]
                    counts[label] += 1
                    counts['total'] += 1
        
        return counts

# Quick test if run directly
if __name__ == "__main__":
    detector = VehicleDetector()
    print("Detector loaded successfully.")
