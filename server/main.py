from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import sys

app = FastAPI()

plates = []

class PlatePayload(BaseModel):
    camera_id: int
    plate_number: str
    bbox: list[int]
    timestamp: str
    frame: str | None = None

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html = """
    <!DOCTYPE html>
    <html>

    <head>

        <title>ANPR Dashboard</title>

        <style>

            body {
                background: #111827;
                color: white;
                font-family: Arial;
                padding: 20px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                background: #1f2937;
            }

            th, td {
                border-bottom: 1px solid #374151;
                padding: 12px;
                text-align: left;
            }

            th {
                background: #374151;
            }

            .plate {
                color: #60a5fa;
                font-weight: bold;
                unicode-bidi: isolate;
            }
            
            .plate-persian {
                direction: ltr;
                unicode-bidi: bidi-override;
                display: inline-block;
                text-align: left;
                font-family: 'Courier New', monospace;
                letter-spacing: 1px;
            }

            img {
                border-radius: 8px;
                max-width: 500px;
            }

            button {
                background: #2563eb;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin-bottom: 20px;
            }

        </style>

    </head>

    <body>

        <h1>License Plate Dashboard</h1>

        <button onclick="clearPlates()">
            Clear All
        </button>

        <table>

            <thead>

                <tr>
                    <th>#</th>
                    <th>Camera</th>
                    <th>Plate</th>
                    <th>Bounding Box</th>
                    <th>Timestamp</th>
                    <th>Frame</th>
                </tr>

            </thead>

            <tbody id="table-body">

            </tbody>

        </table>

        <script>

            async function loadPlates() {

                const response =
                    await fetch('/api/plates')

                const plates =
                    await response.json()

                const tableBody =
                    document.getElementById('table-body')

                tableBody.innerHTML = ''

                plates.reverse().forEach((plate, index) => {

                    let imageHtml = ""

                    if (plate.frame) {

                        imageHtml = `
                            <img
                                src="data:image/jpeg;base64,${plate.frame}"
                                width="500"
                            />
                        `
                    }

                    const plateNumber = plate.plate_number;
                    const isPersian = /[\\u0600-\\u06FF\\uFB50-\\uFDFF\\uFE70-\\uFEFF]/.test(plateNumber);
                    
                    let plateHtml;
                    if (isPersian) {
                        plateHtml = `<span class="plate-persian" style="direction: ltr; unicode-bidi: bidi-override;">${plateNumber}</span>`;
                    } else {
                        plateHtml = plateNumber;
                    }

                    tableBody.innerHTML += `
                        <tr>
                            <td>${index + 1}</td>
                            <td>
                                ${plate.camera_id}
                            </td>
                            <td class="plate">
                                ${plateHtml}
                            </td>
                            <td>
                                ${JSON.stringify(plate.bbox)}
                            </td>
                            <td>
                                ${plate.timestamp}
                            </td>
                            <td>
                                ${imageHtml}
                            </td>
                        </tr>
                    `
                })
            }

            async function clearPlates() {

                await fetch('/api/plates', {
                    method: 'DELETE'
                })

                loadPlates()
            }

            setInterval(loadPlates, 1000)

            loadPlates()

        </script>

    </body>

    </html>
    """
    return HTMLResponse(content=html)

@app.get("/api/plates")
async def get_plates():
    return plates

@app.post("/api/plates")
async def receive_plate(payload: PlatePayload):
    data = {
        "camera_id": payload.camera_id,
        "plate_number": payload.plate_number,
        "bbox": payload.bbox,
        "timestamp": payload.timestamp,
        "frame": payload.frame,
        "received_at": datetime.utcnow().isoformat()
    }
    plates.append(data)
    print(f"[RECEIVED] CAM={payload.camera_id} PLATE={payload.plate_number}")
    return {"status": "success"}

@app.delete("/api/plates")
async def clear_plates():
    plates.clear()
    return {"status": "success"}

if __name__ == "__main__":
    # Check if running as compiled executable
    is_frozen = getattr(sys, 'frozen', False)
    
    # For frozen executable, pass the app object directly instead of string
    if is_frozen:
        # Running as EXE - pass app object directly
        uvicorn.run(
            app,  # Pass the app object directly, not a string
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for EXE
            log_level="info"
        )
    else:
        # Running as script - can use string reference with reload
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )