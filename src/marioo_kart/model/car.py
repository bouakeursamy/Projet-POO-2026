"""Voiture d'un joueur : position, vitesse et image."""

import pygame
import math
from constants import (
    CAR_ACCELERATION, CAR_WIDTH, CAR_HEIGHT, TILE_SIZE
)


class Car:
    """Voiture pilotée par un joueur.

    Parameters
    ----------
    start_col : int
        Colonne de la case de départ.
    start_row : int
        Ligne de la case de départ.
    """

    def __init__(self, start_col: int, start_row: int):
        # la voiture part du centre de sa case de départ, en pixels
        self.x = start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = start_row * TILE_SIZE + TILE_SIZE // 2
        # vitesse en pixels par frame, angle en degrés
        self.speed: float = 0.0
        self.angle: float = 0.0
        self.sprite = self.build_sprite()

    def accelerate(self) -> None:
        """Augmente la vitesse d'un cran, à chaque frame où on accélère."""
        self.speed += CAR_ACCELERATION

    def update_position(self) -> None:
        """Déplace la voiture d'une frame selon sa vitesse."""
        # l'axe y de pygame va vers le bas : la voiture descend l'écran
        self.y += self.speed

    def build_sprite(self) -> pygame.Surface:
        """Crée l'image de la voiture : un rectangle rouge arrondi.

        Returns
        -------
        pygame.Surface
            Image de la voiture, sur un fond transparent.
        """
        # SRCALPHA garde le fond transparent autour du rectangle
        surf = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 0, 0), (0, 0, CAR_WIDTH,
                         CAR_HEIGHT), border_radius=5)
        return surf

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        """Renvoie l'image tournée selon l'angle, et sa place à l'écran.

        Returns
        -------
        tuple[pygame.Surface, pygame.Rect]
            L'image tournée et le rectangle centré sur la voiture.
        """
        # pygame tourne l'image dans le sens trigonométrique : le signe
        # moins la fait tourner dans le sens des aiguilles d'une montre
        rotated = pygame.transform.rotate(self.sprite, -self.angle)
        # l'image tournée est plus grande : on la recentre sur la voiture
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        return rotated, rect
