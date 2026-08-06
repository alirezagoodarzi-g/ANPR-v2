from datetime import datetime

from utils.duplicate_cache import DuplicateCache
from utils.image_encoder import (
    encode_frame_to_base64
)


class PlateService:

    def __init__(
        self,
        detector,
        ocr,
        api_client,
        offline_queue,
        logger,
        app_config,
        api_config
    ):

        self.detector = detector
        self.ocr = ocr
        self.api_client = api_client
        self.offline_queue = offline_queue
        self.logger = logger
        self.app_config = app_config
        self.api_config = api_config

        self.duplicate_cache = DuplicateCache(
            app_config[
                "duplicate_timeout_seconds"
            ]
        )

    def process_frame(
        self,
        frame,
        camera_id
    ):

        detections = self.detector.detect(
            frame
        )

        for detection in detections:

            plate_text = self.ocr.read_text(
                detection.crop
            )

            if not plate_text:
                continue

            if self.duplicate_cache.is_duplicate(
                plate_text
            ):

                self.logger.info(
                    f"[CAM {camera_id}] "
                    f"Duplicate skipped: "
                    f"{plate_text}"
                )

                continue

            timestamp = (
                datetime.utcnow().isoformat()
            )

            frame_base64 = None

            if self.api_config.get(
                "send_full_frame",
                False
            ):

                frame_base64 = (
                    encode_frame_to_base64(
                        frame,
                        jpeg_quality=self.api_config.get(
                            "jpeg_quality",
                            70
                        ),
                        max_width=self.api_config.get(
                            "max_frame_width",
                            1280
                        )
                    )
                )

            payload = {
                "camera_id": camera_id,
                "plate_number": plate_text,
                "bbox": detection.bbox,
                "timestamp": timestamp,
                "frame": frame_base64
            }

            try:

                self.api_client.send_plate(
                    payload
                )

                self.logger.info(
                    f"[CAM {camera_id}] "
                    f"Plate sent: {plate_text}"
                )

            except Exception as e:

                self.logger.error(
                    f"[CAM {camera_id}] "
                    f"API Error: {e}"
                )

                self.offline_queue.add(
                    payload
                )

                self.logger.warning(
                    f"[CAM {camera_id}] "
                    f"Saved to offline queue"
                )