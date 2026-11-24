class StartBlock:
    """Représente une position de départ sur le circuit."""

    def __init__(self, player: int) -> None:
        """Initialise le bloc de départ du joueur."""
        self.letter = str(player)