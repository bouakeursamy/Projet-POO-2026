class Checkpoint:
    """Représente un point de passage du circuit."""

    def __init__(self, number: int) -> None:
        """Initialise le numéro du checkpoint."""
        self.letter = "C"
        self.number = number