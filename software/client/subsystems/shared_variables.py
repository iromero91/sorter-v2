from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from subsystems.classification.known_object import KnownObject


class SharedVariables:
    def __init__(self):
        self.classification_ready: bool = True
        self.distribution_ready: bool = True
        self.exiting_piece: Optional["KnownObject"] = None
