from constants import GameState, GRID_ROWS, GRID_COLS
from model.car import Car
from model.circuit import Circuit
from model.road_tile import RoadTile
from model.terrain import Road, Grass, Dirt, Ice, Void
from model.checkpoint import Checkpoint
from model.finish_line import FinishLine
from model.start_block import StartBlock
from model.boost import Boost


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
        for row_idx in range(1, 4):
            grid[row_idx][10].block = Checkpoint(1)
        for col_idx in range(12, 15):
            grid[5][col_idx].block = Checkpoint(2)
        for row_idx in range(8, 11):
            grid[row_idx][9].block = Checkpoint(3)
        for col_idx in range(1, 4):
            grid[6][col_idx].block = Checkpoint(4)
        for row_idx in range(1,4):
            grid[row_idx][4].block = FinishLine()

        grid[1][3].block = StartBlock(1)
        grid[2][3].block = StartBlock(2)
        grid[1][11].block = Boost()
        grid[10][8].block = Boost()
        self.circuit = Circuit(grid=grid, name="Circuit 1")
        self.spawn_car()

    def spawn_car(self) -> None:
        self.car = Car(7, 1)

    def update(self) -> None:
        if self.state != GameState.RACING or self.circuit is None:
            return
        self.car.update_position()
