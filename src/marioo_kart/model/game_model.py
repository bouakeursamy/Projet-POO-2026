from constants import GameState, GRID_ROWS, GRID_COLS, TILE_SIZE, FPS
from model.car import Car
from model.circuit import Circuit
from model.road_tile import RoadTile


class GameModel:

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.car: Car | None = None

    def load_circuit(self) -> None:
        grid = [[RoadTile(col=col_idx, row=row_idx)
         for col_idx in range(GRID_COLS)]
        for row_idx in range(GRID_ROWS)]
        self.circuit = Circuit(grid=grid, name="Circuit 1")
        self.spawn_car()

    def spawn_car(self) -> None:
        # centre de la case (colonne 7, ligne 1), en pixels
        x = 7 * TILE_SIZE + TILE_SIZE / 2
        y = 1 * TILE_SIZE + TILE_SIZE / 2
        self.car = Car(1, x, y)

    def update(self) -> None:
        if self.state != GameState.RACING or self.circuit is None:
            return
        # durée d'une frame, en attendant que le contrôleur donne dt
        self.car.update(1 / FPS)
