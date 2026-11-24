class Race:
    """Gère les tours, les checkpoints et le vainqueur."""

    def __init__(self) -> None:
        """Initialise les informations de la course."""
        self.laps: list[int] = [0, 0]
        self.checkpoints: list[int] = [0, 0]
        self.total_laps: int = 3
        self.total_checkpoints: int = 4
        self.winner: int | None = None

    def pass_checkpoint(self, player: int,
                        checkpoint_number: int) -> None:
        """Valide un checkpoint franchi dans le bon ordre."""
        if self.winner is not None:
            return

        index = player - 1

        if checkpoint_number == self.checkpoints[index] + 1:
            self.checkpoints[index] += 1

    def pass_finish_line(self, player: int) -> None:
        """Compte un tour après les quatre checkpoints."""
        if self.winner is not None:
            return

        index = player - 1

        if self.checkpoints[index] == self.total_checkpoints:
            self.laps[index] += 1
            self.checkpoints[index] = 0

            if self.laps[index] >= self.total_laps:
                self.winner = player