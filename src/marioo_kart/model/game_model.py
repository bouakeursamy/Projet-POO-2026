from constants import GameState, GRID_ROWS, GRID_COLS, TILE_SIZE, FPS
from model.car import Car
from model.circuit import Circuit
from model.road_tile import RoadTile
from model.terrain import Road, Grass, Dirt, Ice, Void


class GameModel:

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.car: Car | None = None

    def load_circuit(self) -> None:
        """Construit un circuit rectangulaire avec cinq terrains."""
        grid = []

        for row_idx in range(GRID_ROWS):
            row = []

            for col_idx in range(GRID_COLS):
                inside = (1 <= row_idx <= 10 and 1 <= col_idx <= 14)
                border = (row_idx <= 3 or row_idx >= 8
                          or col_idx <= 3 or col_idx >= 12)

                if inside and border:
                    terrain = Road()
                else:
                    terrain = Grass()

                if 2 <= row_idx <= 3 and 5 <= col_idx <= 8:
                    terrain = Ice()
                elif 8 <= row_idx <= 9 and 4 <= col_idx <= 7:
                    terrain = Dirt()
                elif row_idx in (0, 11) and col_idx in (0, 15):
                    terrain = Void()

                tile = RoadTile(col_idx, row_idx, terrain)
                row.append(tile)

            grid.append(row)
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
