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

    def __init__(self):
        self.mapping = PLAYER1_MAPPING

    def get_inputs(self) -> dict:
        keys = pygame.key.get_pressed()
        p = {action: False for action in self.mapping.values()}

        for key, action in self.mapping.items():
            if keys[key]:
                p[action] = True

        return p
