import cv2


class CameraStream:

    def __init__(self, source):

        self.source = source

        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Failed to open camera source: {source}"
            )

    def read(self):

        success, frame = self.cap.read()

        if not success:
            raise RuntimeError(
                f"Failed to read frame from source: {self.source}"
            )

        return frame

    def release(self):
        self.cap.release()