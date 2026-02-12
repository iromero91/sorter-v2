import os
from dotenv import load_dotenv

load_dotenv()


class GlobalConfig:
    db_path: str
    data_dir: str

    def __init__(self):
        pass


def mkGlobalConfig() -> GlobalConfig:
    gc = GlobalConfig()
    gc.db_path = os.environ["DB_PATH"]
    gc.data_dir = os.environ["DATA_DIR"]
    return gc
