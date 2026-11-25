"""Lecture du clavier : touches et actions des deux joueurs."""

import pygame


PLAYER1_MAPPING = {
    pygame.K_z: "accelerate",
    pygame.K_w: "accelerate",
    pygame.K_s: "brake",
    pygame.K_q: "turn_left",
    pygame.K_a: "turn_left",
    pygame.K_d: "turn_right",
}

PLAYER2_MAPPING = {
    pygame.K_UP: "accelerate",
    pygame.K_DOWN: "brake",
    pygame.K_LEFT: "turn_left",
    pygame.K_RIGHT: "turn_right",
}


class InputHandler:
    """Lit le clavier et renvoie les actions des deux joueurs."""

    def __init__(self):
        self.player1_mapping = PLAYER1_MAPPING
        self.player2_mapping = PLAYER2_MAPPING

    def get_inputs(self) -> tuple[dict[str, bool], dict[str, bool]]:
        """Renvoie les actions du joueur 1, puis celles du joueur 2.

        Returns
        -------
        tuple[dict[str, bool], dict[str, bool]]
            Les actions du joueur 1 et celles du joueur 2.
        """
        player1_actions = self._read_actions(self.player1_mapping)
        player2_actions = self._read_actions(self.player2_mapping)
        return player1_actions, player2_actions

    def _read_actions(self, mapping: dict[int, str]) -> dict[str, bool]:
        """Renvoie les actions d'un joueur.

        Parameters
        ----------
        mapping : dict[int, str]
            Les touches du joueur et leur action.

        Returns
        -------
        dict[str, bool]
            True pour chaque action dont la touche est appuyée.
        """
        keys = pygame.key.get_pressed()
        actions = {action: False for action in mapping.values()}
        for key, action in mapping.items():
            if keys[key]:
                actions[action] = True
        return actions
