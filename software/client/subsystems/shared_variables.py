class SharedVariables:
    def __init__(self):
        self.classification_ready: bool = True
        self.distribution_ready: bool = True
        self.piece_at_classification: bool = False
        self.piece_at_distribution: bool = False
