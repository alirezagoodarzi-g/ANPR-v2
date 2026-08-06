print("Starting License Plate Recognition System")

import multiprocessing
import threading
import time
import os

print("Loading path")
from pathlib import Path

print("Importing hezar models")
from hezar.models import Model

print("Importing core modules")
from core.camera import CameraStream
from core.detector import PlateDetector
from core.ocr import PlateOCR
from core.api_client import APIClient
from core.config_loader import load_config

print("Importing services")
from services.plate_service import PlateService
from services.retry_worker import RetryWorker

print("Importing utils")
from utils.logger import setup_logger
from utils.offline_queue import OfflineQueue

os.environ["POLARS_SKIP_CPU_CHECK"] = "1"


def run_camera(camera_config, config):

    logger = setup_logger(
        config["app"]["log_level"]
    )

    camera_id = camera_config["id"]

    logger.info(
        f"Starting camera {camera_id} "
        f"(PID={os.getpid()})"
    )

    camera = None

    try:

        # =========================
        # Validate Model Paths
        # =========================

        yolo_path = Path(
            config["yolo"]["model_path"]
        )

        ocr_path = Path(
            config["ocr"]["model_path"]
        )

        if not yolo_path.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {yolo_path}"
            )

        if not ocr_path.exists():
            raise FileNotFoundError(
                f"OCR model not found: {ocr_path}"
            )

        logger.info("Model paths validated")

        # =========================
        # Camera
        # =========================

        camera = CameraStream(
            camera_config["source"]
        )

        logger.info("Camera initialized")

        # =========================
        # Detector
        # =========================

        detector = PlateDetector(
            model_path=str(yolo_path),
            confidence=config["yolo"]["confidence"],
            iou=config["yolo"]["iou"],
            device=config["yolo"]["device"]
        )

        logger.info("YOLO model loaded")

        # =========================
        # OCR
        # =========================

        ocr_model = Model.load(
            str(ocr_path)
        )

        ocr = PlateOCR(
            ocr_model
        )

        logger.info("OCR model loaded")

        # =========================
        # API Client
        # =========================

        api_client = None

        if config["api"]["enabled"]:
            api_client = APIClient(
                url=config["api"]["url"],
                timeout=config["api"]["timeout"]
            )

        # =========================
        # Offline Queue
        # =========================

        offline_queue = OfflineQueue(
            file_path=config["queue"]["file_path"],
            max_size=config["queue"]["max_size"]
        )

        # =========================
        # Retry Worker
        # =========================

        retry_worker = RetryWorker(
            api_client=api_client,
            queue=offline_queue,
            logger=logger,
            retry_interval=config["api"][
                "retry_interval_seconds"
            ]
        )

        threading.Thread(
            target=retry_worker.start,
            daemon=True
        ).start()

        logger.info(
            "Retry worker started"
        )

        # =========================
        # Plate Service
        # =========================

        service = PlateService(
            detector=detector,
            ocr=ocr,
            api_client=api_client,
            offline_queue=offline_queue,
            logger=logger,
            app_config=config["app"],
            api_config=config["api"]
        )

        logger.info(
            "Plate service initialized"
        )

        # =========================
        # Main Loop
        # =========================

        frame_counter = 0

        while True:

            frame = camera.read()

            frame_counter += 1

            if (
                frame_counter
                % config["app"]["frame_skip"]
                != 0
            ):
                continue

            service.process_frame(
                frame,
                camera_id
            )

    except KeyboardInterrupt:

        logger.warning(
            f"Camera {camera_id} stopped"
        )

    except Exception as e:

        logger.exception(
            f"Fatal error in camera "
            f"{camera_id}: {e}"
        )

        time.sleep(5)

    finally:

        if camera is not None:
            try:
                camera.release()
            except Exception:
                pass


def main():

    print(
        f"MAIN START "
        f"PID={os.getpid()}"
    )

    print("Loading config...")

    config = load_config()

    print("Config loaded")

    processes = []

    for camera in config["cameras"]:

        print(
            f"Creating process for "
            f"camera {camera['id']}"
        )

        process = multiprocessing.Process(
            target=run_camera,
            args=(camera, config)
        )

        process.start()

        print(
            f"Started process "
            f"PID={process.pid}"
        )

        processes.append(process)

    for process in processes:
        process.join()


if __name__ == "__main__":

    multiprocessing.freeze_support()

    print(
        f"ENTRY POINT "
        f"PID={os.getpid()}"
    )

    main()