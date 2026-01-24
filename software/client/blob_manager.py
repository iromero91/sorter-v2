import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import cv2
import numpy as np

DATA_FILE = Path(__file__).parent / "data.json"
BLOB_DIR = Path(__file__).parent / "blob"


def loadData() -> dict[str, Any]:
    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def saveData(data: dict[str, Any]) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def getMachineId() -> str:
    data = loadData()
    if "machine_id" in data:
        return data["machine_id"]

    old_machine_id_file = Path.home() / ".sorter_machine_id"
    if old_machine_id_file.exists():
        machine_id = old_machine_id_file.read_text().strip()
        data["machine_id"] = machine_id
        saveData(data)
        return machine_id

    machine_id = str(uuid.uuid4())
    data["machine_id"] = machine_id
    saveData(data)
    return machine_id


def getStepperPosition(name: str) -> int:
    data = loadData()
    return data.get("stepper_positions", {}).get(name, 0)


def setStepperPosition(name: str, position_steps: int) -> None:
    data = loadData()
    if "stepper_positions" not in data:
        data["stepper_positions"] = {}
    data["stepper_positions"][name] = position_steps
    saveData(data)


def getBinCategories() -> list[list[list[str | None]]] | None:
    data = loadData()
    return data.get("bin_categories")


def setBinCategories(categories: list[list[list[str | None]]]) -> None:
    data = loadData()
    data["bin_categories"] = categories
    saveData(data)


CAMERA_NAMES = ["feeder", "classification_bottom", "classification_top"]


class VideoRecorder:
    _run_dir: Path
    _writers: dict[str, cv2.VideoWriter]
    _fps: int
    _frame_size: tuple[int, int]

    def __init__(self, fps: int = 30, frame_size: tuple[int, int] = (640, 480)):
        self._fps = fps
        self._frame_size = frame_size
        self._writers = {}

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._run_dir = BLOB_DIR / timestamp
        self._run_dir.mkdir(parents=True, exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        for camera in CAMERA_NAMES:
            raw_path = self._run_dir / f"{camera}_raw.mp4"
            annotated_path = self._run_dir / f"{camera}_annotated.mp4"
            self._writers[f"{camera}_raw"] = cv2.VideoWriter(
                str(raw_path), fourcc, fps, frame_size
            )
            self._writers[f"{camera}_annotated"] = cv2.VideoWriter(
                str(annotated_path), fourcc, fps, frame_size
            )

    def writeFrame(
        self, camera: str, raw: Optional[np.ndarray], annotated: Optional[np.ndarray]
    ) -> None:
        if raw is not None:
            raw_key = f"{camera}_raw"
            if raw_key in self._writers:
                resized = cv2.resize(raw, self._frame_size)
                self._writers[raw_key].write(resized)

        if annotated is not None:
            ann_key = f"{camera}_annotated"
            if ann_key in self._writers:
                resized = cv2.resize(annotated, self._frame_size)
                self._writers[ann_key].write(resized)

    def close(self) -> None:
        for writer in self._writers.values():
            writer.release()
        self._writers.clear()
