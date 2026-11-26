import pygame
from constants import TILE_SIZE
from model.terrain import Terrain
from model.boost import Boost


class RoadTile:

    def __init__(self, col: int, row: int, terrain: Terrain) -> None:
        """Initialise la position et le terrain de la case."""
        self.col = col
        self.row = row
        self.terrain = terrain
        self.block = None
        self.sprite: pygame.Surface | None = None

    def get_sprite(self, tile_size: int = TILE_SIZE) -> pygame.Surface:
        if self.sprite and self.sprite.get_width() == tile_size:
            return self.sprite
        surface = pygame.Surface((tile_size, tile_size))
        surface.fill(self.terrain.color)
        pygame.draw.rect(surface, (60, 60, 70), surface.get_rect(), 2)

        # Vérifier si cette case contient un boost
        if isinstance(self.block, Boost):

            # Dessiner un carré jaune au centre de la case
            taille = tile_size // 2
            position = (tile_size - taille) // 2

            pygame.draw.rect(
                surface,
                (255, 215, 0),
                (position, position, taille, taille),
                border_radius=5
            )

            # Écrire la lettre B en noir au centre du carré
            police = pygame.font.Font(None, tile_size // 2)
            texte = police.render("B", True, (0, 0, 0))
            rectangle_texte = texte.get_rect(
                center=(tile_size // 2, tile_size // 2)
            )
            surface.blit(texte, rectangle_texte)


        self.sprite = surface
        return self.sprite
