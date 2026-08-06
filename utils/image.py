import cv2
import os
from datetime import datetime


def save_debug_image(image, folder, prefix="debug"):

    os.makedirs(folder, exist_ok=True)

    filename = (
        f"{prefix}_"
        f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    )

    path = os.path.join(folder, filename)

    cv2.imwrite(path, image)