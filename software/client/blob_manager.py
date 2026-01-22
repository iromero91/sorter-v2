import json
import uuid
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).parent / "data.json"


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
