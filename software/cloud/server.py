import os
import sqlite3
import json
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from typing import Optional

from global_config import mkGlobalConfig, GlobalConfig

gc = mkGlobalConfig()

app = FastAPI()


@app.get("/health")
def healthCheck():
    return {"status": "ok"}


@app.post("/captures")
async def createCapture(
    id: str = Form(...),
    machine_id: str = Form(...),
    run_id: str = Form(...),
    camera_name: str = Form(...),
    source: str = Form(...),
    raw_img: UploadFile = File(...),
    annotated_img: UploadFile = File(...),
    segmentation_data: Optional[UploadFile] = File(None),
):
    capture_dir = os.path.join(gc.data_dir, machine_id, run_id)
    os.makedirs(capture_dir, exist_ok=True)

    raw_name = raw_img.filename
    raw_bytes = await raw_img.read()
    with open(os.path.join(capture_dir, raw_name), "wb") as f:
        f.write(raw_bytes)

    annotated_name = annotated_img.filename
    ann_bytes = await annotated_img.read()
    with open(os.path.join(capture_dir, annotated_name), "wb") as f:
        f.write(ann_bytes)

    seg_name = None
    if segmentation_data is not None:
        seg_name = segmentation_data.filename
        seg_bytes = await segmentation_data.read()
        with open(os.path.join(capture_dir, seg_name), "wb") as f:
            f.write(seg_bytes)

    created_at = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(gc.db_path)
    conn.execute(
        """
        INSERT INTO captures (id, machine_id, run_id, camera_name, source, created_at, raw_img_name, annotated_img_name, segmentation_data_filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (id, machine_id, run_id, camera_name, source, created_at, raw_name, annotated_name, seg_name),
    )
    conn.commit()
    conn.close()

    return {"id": id}


@app.post("/logs")
async def uploadLogs(
    machine_id: str = Form(...),
    run_id: str = Form(...),
    entries: str = Form(...),
):
    log_dir = os.path.join(gc.data_dir, machine_id, run_id, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_entries = json.loads(entries)
    
    current_part = 1
    max_file_size = 1024 * 1024  # 1MB per log file
    
    while True:
        log_filename = f"logs_part_{current_part:03d}.txt"
        log_path = os.path.join(log_dir, log_filename)
        
        if not os.path.exists(log_path):
            break
        
        if os.path.getsize(log_path) < max_file_size:
            break
        
        current_part += 1
    
    log_path = os.path.join(log_dir, f"logs_part_{current_part:03d}.txt")
    
    with open(log_path, "a", encoding="utf-8") as f:
        for entry in log_entries:
            timestamp_str = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp_str}] [{entry['level']}] {entry['message']}\n")
    
    return {"success": True, "part": current_part}


def main():
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
