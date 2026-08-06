# ANPR-v2 – Automatic Number Plate Recognition System

## Overview

ANPR-v2 is a Python-based **Automatic Number Plate Recognition (ANPR)** system that detects vehicle license plates from one or more camera streams, extracts the plate text using OCR, and sends the recognition results to a REST API.

The project is designed to be reliable in production environments by supporting:

* Real-time camera processing
* YOLO-based license plate detection
* OCR-based plate recognition
* Duplicate plate filtering
* Offline queueing
* Automatic retry of failed API requests
* Configurable multi-camera support
* Debug image saving
* Web dashboard/server

---

## Features

* 🚗 Real-time license plate detection
* 🔍 YOLO object detection model
* 📝 OCR recognition using Hezar
* 📷 USB/IP camera support
* 🌐 REST API integration
* 📦 Offline request queue
* 🔄 Automatic retry service
* 🚫 Duplicate plate suppression
* ⚙ JSON-based configuration
* 📊 Logging support
* 🧵 Multi-process camera handling

---

## Project Structure

```text
ANPR-v2/
│
├── core/
│   ├── api_client.py
│   ├── camera.py
│   ├── config_loader.py
│   ├── detector.py
│   └── ocr.py
│
├── services/
│   ├── plate_service.py
│   └── retry_worker.py
│
├── utils/
│   ├── duplicate_cache.py
│   ├── image.py
│   ├── image_encoder.py
│   ├── logger.py
│   └── offline_queue.py
│
├── server/
│   ├── main.py
│   └── templates/
│
├── weights/
│   └── best.pt
│
├── OCR_model/
│
├── config.json
├── main.py
└── requirements.txt
```

---

# System Workflow

1. Capture frames from the configured camera.
2. Skip frames according to the configured frame interval.
3. Detect license plates using the YOLO model.
4. Crop detected plates.
5. Recognize plate text using the OCR model.
6. Filter duplicate detections.
7. Encode images (optional).
8. Send recognition data to the API.
9. Store failed requests in the offline queue.
10. Retry queued requests automatically when the API becomes available.

---

# Technologies

* Python 3
* YOLO
* Hezar OCR
* OpenCV
* Requests
* Multiprocessing
* Threading
* REST API

---

# Requirements

* Python 3.10+
* Camera device or RTSP stream
* YOLO model (`best.pt`)
* OCR model directory
* Internet/network connection (optional for API upload)

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
cd ANPR-v2
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Configuration

The application is configured using `config.json`.

## Application

```json
"app": {
    "frame_skip": 5,
    "duplicate_timeout_seconds": 10,
    "save_debug_images": false,
    "debug_image_dir": "debug",
    "log_level": "INFO"
}
```

| Setting                   | Description                                      |
| ------------------------- | ------------------------------------------------ |
| frame_skip                | Number of frames skipped between processing      |
| duplicate_timeout_seconds | Time before the same plate can be detected again |
| save_debug_images         | Save detection images for debugging              |
| debug_image_dir           | Directory for saved debug images                 |
| log_level                 | Logging level                                    |

---

## API

```json
"api": {
    "enabled": true,
    "url": "http://127.0.0.1:8000/api/plates",
    "timeout": 5,
    "retry_interval_seconds": 10
}
```

| Setting                | Description                        |
| ---------------------- | ---------------------------------- |
| enabled                | Enable API communication           |
| url                    | Endpoint for plate data            |
| timeout                | HTTP timeout                       |
| retry_interval_seconds | Retry interval for queued requests |

Optional image settings:

* send_full_frame
* jpeg_quality
* max_frame_width

---

## Queue

```json
"queue": {
    "enabled": true,
    "max_size": 100,
    "file_path": "cache/pending.json"
}
```

Failed requests are stored locally and resent automatically.

---

## YOLO

```json
"yolo": {
    "model_path": "weights/best.pt",
    "confidence": 0.5,
    "iou": 0.7,
    "device": "cpu"
}
```

---

## OCR

```json
"ocr": {
    "model_path": "OCR_model"
}
```

---

## Cameras

Example:

```json
"cameras": [
    {
        "id": 1,
        "source": 1
    }
]
```

The `source` may be:

* Camera index (0, 1, 2, ...)
* Video file
* RTSP stream
* HTTP stream

---

# Running the Application

Start the ANPR service:

```bash
python main.py
```

The application will:

* Load the configuration
* Validate model paths
* Start camera processes
* Load YOLO
* Load OCR
* Start the retry worker
* Begin processing video streams

---

# Web Server

A lightweight web server is included under the `server/` directory.

Run it with:

```bash
python server/main.py
```

The server can be used to host a simple dashboard or provide API endpoints, depending on your deployment.

---

# Logging

Logging is configurable through:

```json
"log_level": "INFO"
```

Typical levels include:

* DEBUG
* INFO
* WARNING
* ERROR

---

# Offline Mode

If the API is unavailable:

* Recognition results are saved locally.
* Data is written to the offline queue.
* A background retry worker periodically attempts to resend pending records.

This ensures detections are not lost during network interruptions.

---

# Author

Developed as an Automatic Number Plate Recognition (ANPR) solution using YOLO-based detection and OCR for real-time vehicle identification.
