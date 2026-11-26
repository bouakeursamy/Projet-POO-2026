import pygame
import sys
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    GameState
)
from model.game_model import GameModel
from model.car import Car
from view.game_view import GameView
from controller.input_handler import InputHandler


class GameController:

    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.model = GameModel()
        self.view = GameView(self.screen)
        self.input_handler = InputHandler()
        self.running = True

    def run(self) -> None:
        """Fait tourner la boucle principale du jeu."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.render()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

    def handle_keydown(self, key: int) -> None:

        state = self.model.state

        if state == GameState.MENU:
            self.handle_menu_key(key)
        elif state == GameState.SELECTION:
            self.handle_selection_key(key)
        elif state == GameState.RACING:
            self.handle_racing_key(key)
        elif state == GameState.FINISHED:
            self.handle_finished_key(key)

    def handle_menu_key(self, key: int) -> None:
        """
        Gère les touches du menu principal.

        Parameters
        ----------
        key : int
            Code pygame de la touche appuyée.
        """
        if key == pygame.K_RETURN:
            self.model.state = GameState.SELECTION
        elif key == pygame.K_ESCAPE:
            self.quit()

    def handle_selection_key(self, key: int) -> None:
        """
        Gère les touches de l'écran de choix du circuit.

        Parameters
        ----------
        key : int
            Code pygame de la touche appuyée.
        """
        index = self.model.selected_index
        count = len(self.model.circuit_names)
        if key == pygame.K_UP:
            self.model.selected_index = (index - 1) % count
        elif key == pygame.K_DOWN:
            self.model.selected_index = (index + 1) % count
        elif key == pygame.K_RETURN:
            self.model.start_race(index)
        elif key == pygame.K_ESCAPE:
            self.model.state = GameState.MENU

    def handle_racing_key(self, key: int) -> None:
        """
        Gère les touches pendant la course.

        Parameters
        ----------
        key : int
            Code pygame de la touche appuyée.
        """
        if key == pygame.K_ESCAPE:
            self.model.state = GameState.MENU

    def handle_finished_key(self, key: int) -> None:
        """
        Gère les touches de l'écran de fin de course.

        Parameters
        ----------
        key : int
            Code pygame de la touche appuyée.
        """
        if key == pygame.K_RETURN or key == pygame.K_ESCAPE:
            self.model.state = GameState.MENU

    def update(self, dt: float) -> None:
        """
        Fait avancer la course d'une image.

        Parameters
        ----------
        dt : float
            Temps écoulé depuis l'image précédente, en secondes.
        """
        if self.model.state != GameState.RACING:
            return

        p1_input, p2_input = self.input_handler.get_inputs()
        self.apply_input(self.model.cars[0], p1_input)
        self.apply_input(self.model.cars[1], p2_input)
        self.model.update(dt)
        if self.model.race.winner is not None:
            self.model.state = GameState.FINISHED

    def apply_input(self, car: Car, player_input: dict[str, bool]) -> None:
        """
        Applique les actions d'un joueur à sa voiture.

        Parameters
        ----------
        car : Car
            Voiture du joueur.
        player_input : dict[str, bool]
            Actions du joueur, True si la touche est appuyée.
        """
        if player_input['accelerate']:
            car.accelerate()
        if player_input['brake']:
            car.brake()
        if player_input['turn_left']:
            car.turn_left()
        if player_input['turn_right']:
            car.turn_right()

    def render(self) -> None:
        self.view.draw(self.model)

    def quit(self) -> None:
        self.running = False
        pygame.quit()
        sys.exit()
