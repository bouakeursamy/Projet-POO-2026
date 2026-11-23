"""Point d'entrée du jeu : lance pygame et la boucle de jeu."""

import pygame
from controller.game_controller import GameController


def main() -> None:
    """Initialise pygame, lance la boucle de jeu puis ferme pygame."""
    pygame.init()
    pygame.display.set_caption("Projet Python - Jeu de course 2D")

    controller = GameController()
    # run() ne s'arrête que quand on quitte le jeu
    controller.run()

    pygame.quit()


if __name__ == "__main__":
    main()
