from typing import Callable, Optional
import threading
import numpy as np
from global_config import GlobalConfig


class BrickognizeClient:
    def __init__(self, gc: GlobalConfig):
        self.gc = gc

    def classify(
        self,
        top_image: np.ndarray,
        bottom_image: np.ndarray,
        callback: Callable[[Optional[str]], None],
    ) -> None:
        thread = threading.Thread(
            target=self._doClassify,
            args=(top_image, bottom_image, callback),
            daemon=True,
        )
        thread.start()

    def _doClassify(
        self,
        top_image: np.ndarray,
        bottom_image: np.ndarray,
        callback: Callable[[Optional[str]], None],
    ) -> None:
        self.gc.logger.info("Brickognize: classifying piece (stub)")
        callback(None)
