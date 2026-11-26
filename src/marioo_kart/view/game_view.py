import math
import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE, CAR_WIDTH, CAR_HEIGHT,
    COLOR_BG, COLOR_TEXT, COLOR_ACCENT, COLOR_PANEL, COLOR_PANEL_BORDER,
    CAR_COLORS, COLOR_BLOCK_TEXT, GameState
)
from model.car import Car
from model.road_tile import RoadTile
from model.game_model import GameModel


class GameView:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self, model: GameModel) -> None:
        self.screen.fill(COLOR_BG)
        if model.state == GameState.MENU:
            self._draw_menu(model)
        elif model.state == GameState.RACING:
            self._draw_racing(model)
        pygame.display.flip()

    def _draw_menu(self, model: GameModel) -> None:
        cx = WINDOW_WIDTH // 2

        title_surf = self.font.render(
            "Jeu de course 2D", True, COLOR_ACCENT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(cx, 160)))

        options = [("JOUER (Enter)", GameState.RACING),
                   ("QUITTER (Escape)", None)]
        for i, (label, _) in enumerate(options):
            y = 320 + i * 80
            rect = pygame.Rect(cx - 140, y - 25, 280, 50)
            pygame.draw.rect(self.screen, COLOR_PANEL, rect, border_radius=8)
            pygame.draw.rect(self.screen, COLOR_PANEL_BORDER,
                             rect, 2, border_radius=8)
            text_surf = self.font.render(
                label, True, COLOR_ACCENT if i == 0 else COLOR_TEXT)
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def _draw_racing(self, model: GameModel) -> None:

        for row in model.circuit.grid:
            for tile in row:
                self._draw_tile(tile)

        if model.circuit is None:
            return
        for index, car in enumerate(model.cars):
            self._draw_car(car, CAR_COLORS[index])

    def _draw_car(self, car: Car, color: tuple[int, int, int]) -> None:
        """Dessine une voiture tournée selon son angle.

        Parameters
        ----------
        car : Car
            Voiture à dessiner.
        color : tuple[int, int, int]
            Couleur de la voiture.
        """
        surf = pygame.Surface((CAR_HEIGHT, CAR_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (0, 0, CAR_HEIGHT, CAR_WIDTH),
                         border_radius=5)
        rotated = pygame.transform.rotate(surf, math.degrees(car.angle))
        rect = rotated.get_rect(center=(int(car.x), int(car.y)))
        self.screen.blit(rotated, rect)

    def _draw_tile(self, tile: RoadTile) -> None:
        """Dessine une case et écrit la lettre de son bloc.

        Parameters
        ----------
        tile : RoadTile
            Case à dessiner.
        """
        rect = pygame.Rect(tile.col * TILE_SIZE, tile.row * TILE_SIZE,
                           TILE_SIZE, TILE_SIZE)
        self.screen.blit(tile.get_sprite(TILE_SIZE), rect)
        if tile.block is None or tile.block.letter == "B":
            return
        label = tile.block.letter
        if label == "C":
            label = label + str(tile.block.number)
        text = self.font.render(label, True, COLOR_BLOCK_TEXT)
        self.screen.blit(text, text.get_rect(center=rect.center))
        