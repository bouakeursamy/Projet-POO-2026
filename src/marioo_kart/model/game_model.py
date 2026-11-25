from constants import GameState, GRID_ROWS, GRID_COLS, TILE_SIZE, FPS
from model.car import Car
from model.circuit import Circuit
from model.road_tile import RoadTile
from model.terrain import Road, Grass, Dirt, Ice, Void
from model.checkpoint import Checkpoint
from model.finish_line import FinishLine
from model.start_block import StartBlock
from model.boost import Boost
from model.race import Race


class GameModel:

    def __init__(self):
        self.state: str = GameState.MENU
        self.circuit: Circuit | None = None
        self.car: Car | None = None
        self.race: Race = Race()
        self.last_blocks: list[str | None] = [None, None]

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
        for row_idx in range(1,4):
            grid[row_idx][10].block = Checkpoint(1)
        for col_idx in range(12,15):
            grid[5][col_idx].block = Checkpoint(2)
        for row_idx in range(8,11):
            grid[row_idx][9].block = Checkpoint(3)
        for col_idx in range(1,4):
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
        # centre de la case (colonne 7, ligne 1), en pixels
        x = 7 * TILE_SIZE + TILE_SIZE / 2
        y = 1 * TILE_SIZE + TILE_SIZE / 2
        self.car = Car(1, x, y)

    def check_car_block(self, car: Car, player: int) -> None:
        """Détecte l'entrée sur un checkpoint ou l'arrivée."""
        if self.circuit is None:
            return

        index = player - 1
        tile = self.circuit.get_tile_at_pixel(car.x, car.y)
        block = tile.block if tile is not None else None

        if isinstance(block, Checkpoint):
            block_id = f"C{block.number}"
        elif isinstance(block, FinishLine):
            block_id = "L"
        else:
            self.last_blocks[index] = None
            return

        if block_id == self.last_blocks[index]:
            return

        self.last_blocks[index] = block_id

        if isinstance(block, Checkpoint):
            self.race.pass_checkpoint(player, block.number)
        else:
            self.race.pass_finish_line(player)
    def update(self) -> None:
        if self.state != GameState.RACING or self.circuit is None:
            return

        # durée d'une frame, en attendant que le contrôleur donne dt
        # le terrain sous la voiture change sa traction
        tile = self.circuit.get_tile_at_pixel(self.car.x, self.car.y)
        if tile is not None:
            self.car.update(1 / FPS, tile.terrain)
        self.check_car_block(self.car, 1)