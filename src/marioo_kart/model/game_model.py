from constants import (
    GameState, GRID_ROWS, GRID_COLS, TILE_SIZE, FPS, BOOST_DURATION
)
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
        # Dernière position de réapparition de chaque joueur
        self.last_checkpoint_positions: list[
            tuple[float, float] | None
        ] = [None, None]
        self.circuit_names: list[str] = ["Circuit 1", "Circuit 2"]
        self.selected_index: int = 0

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

    def load_second_circuit(self) -> None:
        """Construit un deuxième circuit avec plusieurs virages."""
        grid = []

        for row_idx in range(GRID_ROWS):
            row = []

            for col_idx in range(GRID_COLS):
                top = 1 <= row_idx <= 3 and 1 <= col_idx <= 10
                left = 1 <= row_idx <= 7 and 1 <= col_idx <= 3
                middle_left = 5 <= row_idx <= 7 and 1 <= col_idx <= 6
                inner = 6 <= row_idx <= 10 and 4 <= col_idx <= 6
                bottom = 8 <= row_idx <= 10 and 4 <= col_idx <= 14
                right = 4 <= row_idx <= 10 and 12 <= col_idx <= 14
                middle = 4 <= row_idx <= 6 and 8 <= col_idx <= 14
                upper = 1 <= row_idx <= 6 and 8 <= col_idx <= 10

                if (top or left or middle_left or inner
                        or bottom or right or middle or upper):
                    terrain = Road()
                else:
                    terrain = Grass()
                if 1 <= row_idx <= 3 and 5 <= col_idx <= 7:
                    terrain = Ice()
                elif 8 <= row_idx <= 10 and 8 <= col_idx <= 10:
                    terrain = Dirt()
                elif row_idx in (0, 11) or col_idx in (0, 15):
                    terrain = Void()
                row.append(RoadTile(col_idx, row_idx, terrain))

            grid.append(row)
        # Checkpoint 1 : décalé d'une case vers la gauche
        for row_idx in range(1, 4):
            grid[row_idx][8].block = Checkpoint(1)

        # Checkpoint 2 : décalé d'une case vers le bas
        for col_idx in range(12, 15):
            grid[6][col_idx].block = Checkpoint(2)

        # Checkpoint 3 : décalé de deux cases vers la gauche
        for row_idx in range(8, 11):
            grid[row_idx][8].block = Checkpoint(3)

        # Checkpoint 4 : décalé d'une case vers le haut
        for col_idx in range(1, 4):
            grid[5][col_idx].block = Checkpoint(4)

        # La ligne d'arrivée
        for row_idx in range(1, 4):
            grid[row_idx][4].block = FinishLine()

        # Les deux positions de départ
        grid[2][2].block = StartBlock(1)
        grid[2][3].block = StartBlock(2)

        # Les deux boosts
        grid[2][7].block = Boost()
        grid[9][13].block = Boost()
        self.circuit = Circuit(grid=grid, name="Circuit 2")
        self.spawn_car()

    def start_race(self, circuit_index: int) -> None:
        """Sélectionne un circuit et démarre une nouvelle course."""
        self.selected_index = circuit_index

        if circuit_index == 0:
            self.load_circuit()
        elif circuit_index == 1:
            self.load_second_circuit()
        else:
            raise ValueError("Indice de circuit invalide")

        self.race = Race()
        self.last_blocks = [None, None]
        self.state = GameState.RACING
    def spawn_car(self) -> None:
        """
        Place la voiture du joueur 1 sur sa case de départ.

        Cette méthode parcourt les cases du circuit chargé
        afin de trouver le bloc StartBlock du joueur 1.

        Lorsque ce bloc est trouvé, elle calcule les coordonnées
        du centre de la case et crée la voiture à cet endroit.

        La position trouvée est également enregistrée comme
        position de réapparition initiale. Ainsi, si le joueur
        tombe dans le vide avant le premier checkpoint, sa
        voiture revient à son point de départ.

        Retour
        ------
        None
            La méthode initialise la voiture et mémorise
            sa position de départ.
        """

        # Vérifier qu'un circuit a été chargé
        if self.circuit is None:
            return

        # Parcourir toutes les lignes du circuit
        for row in self.circuit.grid:

            # Parcourir chaque case de la ligne
            for tile in row:

                # Rechercher le bloc de départ du joueur 1
                if (isinstance(tile.block, StartBlock)
                        and tile.block.letter == "1"):

                    # Calculer les coordonnées du centre de la case
                    x = (tile.col + 0.5) * TILE_SIZE
                    y = (tile.row + 0.5) * TILE_SIZE

                    # Créer la voiture du joueur 1 à cette position
                    self.car = Car(1, x, y)

                    # Mémoriser sa position de réapparition initiale
                    self.last_checkpoint_positions[0] = (x, y)

                    # Arrêter la recherche une fois le départ trouvé
                    return

        raise ValueError("Départ du joueur 1 introuvable")

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
        elif isinstance(block, Boost):
            # Identifier une case de boost avec la lettre B
            block_id = "B"
        else:
            self.last_blocks[index] = None
            return

        if block_id == self.last_blocks[index]:
            return

        self.last_blocks[index] = block_id

        if isinstance(block, Checkpoint):
            # Sauvegarder le nombre de checkpoints déjà validés
            previous_count = self.race.checkpoints[index]

            # Vérifier si le nouveau checkpoint est dans le bon ordre
            self.race.pass_checkpoint(player, block.number)

            # Enregistrer la position seulement si le checkpoint est validé
            if self.race.checkpoints[index] > previous_count:
                self.last_checkpoint_positions[index] = (
                    (tile.col + 0.5) * TILE_SIZE,
                    (tile.row + 0.5) * TILE_SIZE
                )

        elif isinstance(block, FinishLine):
        # Vérifier si le joueur a terminé un tour
            self.race.pass_finish_line(player)

        elif isinstance(block, Boost):
        # Activer le boost pendant la durée prévue
            car.boost_time = BOOST_DURATION

    def check_car_void(self, car: Car, player: int) -> None:
        """
        Vérifie si une voiture est tombée dans une zone vide.

        Cette méthode récupère la case sur laquelle se trouve la
        voiture et vérifie si son terrain est de type Void ou si
        la voiture est sortie des limites du circuit.

        En cas de chute, la voiture est replacée à sa dernière
        position de réapparition enregistrée, correspondant au
        dernier checkpoint validé ou au départ de la course.
        Sa vitesse est remise à zéro pour éviter qu'elle continue
        à se déplacer immédiatement après sa réapparition.

        Paramètres
        ----------
        car : Car
            Voiture dont on souhaite vérifier la position.
        player : int
            Numéro du joueur concerné (1 ou 2).

        Retour
        ------
        None
            La méthode modifie directement la position et la
            vitesse de la voiture lorsque cela est nécessaire.
        """

        # Vérifier qu'un circuit est bien chargé
        if self.circuit is None:
            return

        # Récupérer la case correspondant à la position de la voiture
        tile = self.circuit.get_tile_at_pixel(car.x, car.y)

        # Détecter une sortie du circuit ou une case de terrain vide
        if tile is None or tile.terrain.is_void:

            # Récupérer la position de réapparition du joueur
            index = player - 1
            position = self.last_checkpoint_positions[index]

            # Vérifier qu'une position de réapparition existe
            if position is not None:

                # Replacer la voiture au dernier checkpoint validé
                car.x, car.y = position

                # Annuler sa vitesse pour arrêter son déplacement
                car.vx = 0.0
                car.vy = 0.0

                # Réinitialiser la détection des blocs spéciaux
                self.last_blocks[index] = None
    def update(self) -> None:
        """
        Met à jour le déroulement de la course à chaque image.

        Cette méthode est exécutée uniquement lorsque le jeu est
        en cours et qu'un circuit est chargé.

        Elle actualise la position de la voiture en fonction de
        sa vitesse, puis vérifie les interactions avec les blocs
        spéciaux du circuit : checkpoints, arrivée et boosts.

        Enfin, elle vérifie si la voiture est tombée dans le vide.
        Si nécessaire, elle déclenche sa réapparition au dernier
        checkpoint validé ou à son point de départ.

        Retour
        ------
        None
            La méthode actualise directement les données du jeu.
        """

        # Vérifier que la course est active et qu'un circuit existe
        if self.state != GameState.RACING or self.circuit is None:
            return

        # Actualiser la position de la voiture pendant une frame
        self.car.update(1 / FPS)

        # Détecter les checkpoints, l'arrivée et les boosts
        self.check_car_block(self.car, 1)

        # Vérifier une éventuelle chute dans le vide
        self.check_car_void(self.car, 1)
