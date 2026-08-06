import cv2
import base64


def encode_frame_to_base64(
    frame,
    jpeg_quality=70,
    max_width=1280
):

    h, w = frame.shape[:2]

    if w > max_width:

        scale = max_width / w

        frame = cv2.resize(
            frame,
            (
                int(w * scale),
                int(h * scale)
            )
        )

    success, buffer = cv2.imencode(
        ".jpg",
        frame,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            jpeg_quality
        ]
    )

    if not success:
        return None

    return base64.b64encode(
        buffer.tobytes()
    ).decode("utf-8")