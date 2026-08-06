from ultralytics import YOLO


class Detection:

    def __init__(
        self,
        bbox,
        confidence,
        crop
    ):

        self.bbox = bbox
        self.confidence = confidence
        self.crop = crop


class PlateDetector:

    def __init__(
        self,
        model_path,
        confidence,
        iou,
        device
    ):

        self.model = YOLO(model_path)

        self.confidence = confidence
        self.iou = iou
        self.device = device

    def detect(self, frame):

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            iou=self.iou,
            device=self.device,
            verbose=False
        )

        detections = []

        boxes = results[0].boxes

        for box in boxes:

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            crop = frame[y1:y2, x1:x2]

            detection = Detection(
                bbox=[x1, y1, x2, y2],
                confidence=float(box.conf[0]),
                crop=crop
            )

            detections.append(
                detection
            )

        return detections