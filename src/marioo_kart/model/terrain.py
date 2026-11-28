"""Définit les différents types de terrains du circuit."""


class Terrain:
    """Représente un terrain et ses propriétés physiques."""

    def __init__(self, name: str, color: tuple[int, int, int],
                 traction: float, drift_threshold: float,
                 drift_friction: float) -> None:
        """Initialise les propriétés du terrain."""
        self.name = name
        self.color = color
        self.traction = traction
        self.drift_threshold = drift_threshold
        self.drift_friction = drift_friction
        self.is_void = False
        self.is_solid = False

class Ice(Terrain):
    """Représente la glace, un terrain à faible adhérence."""

    def __init__(self) -> None:
        """Initialise les propriétés de la glace."""
        super().__init__("glace", (180, 220, 255), 0.3, 30.0, 10.0)

class Road(Terrain):
    """Représente la route, un terrain à bonne adhérence."""

    def __init__(self) -> None:
        """Initialise les propriétés de la route."""
        super().__init__("route", (100, 100, 100), 1.0, 760.0, 560.0)

class Grass(Terrain):
    """Représente l'herbe, un terrain à adhérence réduite."""

    def __init__(self) -> None:
        """Initialise les propriétés de l'herbe."""
        super().__init__("herbe", (80, 160, 80), 0.6, 210.0, 150.0)

class Dirt(Terrain):
    """Représente la terre, un terrain à adhérence moyenne."""

    def __init__(self) -> None:
        """Initialise les propriétés de la terre."""
        super().__init__("terre", (150, 100, 60), 0.55, 120.0, 75.0)

class Void(Terrain):
    """Représente une zone vide où la voiture ne peut pas rouler."""

    def __init__(self) -> None:
        """Initialise les propriétés du vide."""
        super().__init__("vide", (20, 20, 30), 0.0, 0.0, 0.0)
        self.is_void = True


class Wall(Terrain):
    """
    Représente un mur infranchissable sur le circuit.

    Un mur est un terrain solide qui empêche les voitures
    de passer à travers lorsqu'une collision est détectée.

    Il se distingue du vide : une voiture doit être bloquée
    par un mur, et non téléportée au dernier checkpoint.
    """

    def __init__(self) -> None:
        """
        Initialise les propriétés physiques et visuelles du mur.

        Le mur possède une couleur rouge foncé pour être
        facilement identifiable sur le circuit.

        Sa propriété is_solid est définie à True afin de
        permettre au modèle de détecter les obstacles.
        """

        # Initialiser les propriétés héritées de Terrain
        super().__init__("mur", (170, 70, 70), 0.0, 0.0, 0.0)

        # Indiquer que le mur est infranchissable
        self.is_solid = True
