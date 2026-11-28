from constants import (
    GameState, GRID_ROWS, GRID_COLS, TILE_SIZE, FPS, BOOST_DURATION
)
from model.car import Car
from model.circuit import Circuit
from model.road_tile import RoadTile
from model.terrain import Road, Grass, Dirt, Ice, Void, Wall
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
        # Liste des voitures participant à la course
        # L'indice 0 correspond au joueur 1 et l'indice 1 au joueur 2
        self.cars: list[Car] = []
        self.last_blocks: list[str | None] = [None, None]
        # Dernière position de réapparition de chaque joueur
        self.last_checkpoint_positions: list[
            tuple[float, float] | None
        ] = [None, None]
        self.circuit_names: list[str] = [
            "Circuit 1",
            "Circuit 2",
            "Circuit 3"
        ]
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

                # Créer une zone de vide au milieu du circuit
                # Remplacer une partie de l'herbe par un trou
                if 5 <= row_idx <= 6 and 6 <= col_idx <= 9:
                    terrain = Void()
                # Ajouter un trou sur la route à droite du circuit
                # Les joueurs peuvent contourner le trou
                if row_idx == 7 and col_idx == 12:
                    terrain = Void()
                # Placer quatre murs aux coins de la zone d'herbe
                # Les murs entourent la zone centrale sans bloquer le circuit
                if row_idx in (4, 7) and col_idx in (4, 11):
                    terrain = Wall()

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
                # Ajouter trois cases de vide au centre du circuit 2
                # Ces obstacles remplacent une partie de l'herbe
                if row_idx == 7 and 9 <= col_idx <= 11:
                    terrain = Void()
                # Ajouter un trou sur la route du bas du circuit 2
                # Les voitures peuvent contourner cet obstacle
                if row_idx == 8 and col_idx == 11:
                    terrain = Void()


                # Ajouter des murs sur le contour intérieur
                # de la zone d'herbe du deuxième circuit

                # Partie horizontale supérieure
                if row_idx == 4 and 4 <= col_idx <= 7:
                    terrain = Wall()

                # Partie verticale à droite
                if 5 <= row_idx <= 7 and col_idx == 7:
                    terrain = Wall()

                # Dernier mur dans le coin inférieur droit
                if row_idx == 7 and col_idx == 8:
                    terrain = Wall()

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
        grid[3][2].block = StartBlock(2)

        # Les deux boosts
        grid[2][7].block = Boost()
        grid[9][13].block = Boost()
        self.circuit = Circuit(grid=grid, name="Circuit 2")
        self.spawn_car()

    def load_third_circuit(self) -> None:
        """
        Construit le troisième circuit du jeu : Le Serpent.

        Ce circuit propose un niveau de difficulté plus élevé grâce
        à plusieurs virages serrés et à des obstacles variés.

        Il comprend :
        - Une route avec plusieurs changements de direction.
        - Des murs en briques délimitant les zones infranchissables.
        - Des zones de glace et de terre modifiant l'adhérence.
        - Des zones de vide représentant des dangers.
        - Quatre checkpoints à franchir dans l'ordre.
        - Une ligne d'arrivée et deux positions de départ.
        - Trois boosts permettant d'accélérer temporairement.

        La méthode construit la grille, place les blocs spéciaux,
        puis initialise les voitures des deux joueurs.
        """

        # ==========================================================
        # 1. CONSTRUCTION DE LA GRILLE ET DU TRACÉ
        # ==========================================================

        grid = []

        # Parcourir chaque ligne de la grille
        for row_idx in range(GRID_ROWS):
            row = []

            # Parcourir chaque colonne de la ligne
            for col_idx in range(GRID_COLS):

                # Définir les différentes sections de la route
                top = 1 <= row_idx <= 2 and 1 <= col_idx <= 12

                right_top = (
                    2 <= row_idx <= 4 and 11 <= col_idx <= 13
                )

                upper_turn = (
                    4 <= row_idx <= 5 and 8 <= col_idx <= 13
                )

                center = (
                    5 <= row_idx <= 7 and 7 <= col_idx <= 9
                )

                lower_turn = (
                    7 <= row_idx <= 8 and 8 <= col_idx <= 13
                )

                right_bottom = (
                    8 <= row_idx <= 10 and 12 <= col_idx <= 14
                )

                bottom = (
                    9 <= row_idx <= 10 and 2 <= col_idx <= 14
                )

                left = (
                    2 <= row_idx <= 9 and 1 <= col_idx <= 3
                )

                # Déterminer si la case appartient au tracé
                is_road = (
                    top or right_top or upper_turn or center
                    or lower_turn or right_bottom or bottom or left
                )

                # Créer une route sur le tracé
                # et des murs sur les autres cases
                if is_road:
                    terrain = Road()
                else:
                    terrain = Wall()

                # 2. BORDURES ET TERRAINS PARTICULIER
                # Première ligne entièrement constituée de briques
                if row_idx == 0:
                    terrain = Wall()

                # Bordures inférieure et latérales en terrain vide
                elif (
                    row_idx == GRID_ROWS - 1
                    or col_idx in (0, GRID_COLS - 1)
                ):
                    terrain = Void()

                # Zone de glace sur la partie supérieure
                elif row_idx == 1 and 5 <= col_idx <= 9:
                    terrain = Ice()

                # Zone de terre sur la partie inférieure
                elif row_idx in (9, 10) and 6 <= col_idx <= 10:
                    terrain = Dirt()

                # 3. OBSTACLES ET ZONES DANGEREUSES
                # Placer les trous à éviter pendant la course
                if (row_idx, col_idx) in (
                    (2, 8),
                    (4, 10),
                    (7, 10),
                ):
                    terrain = Void()

                # Murs dans la partie supérieure du circuit
                if row_idx == 3 and 5 <= col_idx <= 8:
                    terrain = Wall()

                # Murs dans la partie centrale du circuit
                if row_idx == 6 and 10 <= col_idx <= 12:
                    terrain = Wall()

                # Murs dans la partie inférieure du circuit
                if row_idx == 8 and 5 <= col_idx <= 7:
                    terrain = Wall()

                # 4. PERSONNALISATION DES ZONES DU CIRCUIT
                # Bande d'herbe à droite du circuit
                # Colonne 14, de la ligne 1 à la ligne 7
                if col_idx == 14 and 1 <= row_idx <= 7:
                    terrain = Grass()

                # Mur remplaçant l'ancien trou dans la zone de terre
                if row_idx == 9 and col_idx == 7:
                    terrain = Wall()

                # Murs sur une partie de la dernière ligne
                if row_idx == 11 and 6 <= col_idx <= 10:
                    terrain = Wall()

                # Créer la case avec son terrain définitif
                tile = RoadTile(col_idx, row_idx, terrain)
                row.append(tile)

            # Ajouter la ligne complète à la grille
            grid.append(row)

        # 5. PLACEMENT DES BLOCS SPÉCIAUX
        # Checkpoints : passage obligatoire dans l'ordre 1, 2, 3, 4
        # Checkpoint 1 : partie supérieure
        for row_idx in range(1, 3):
            grid[row_idx][7].block = Checkpoint(1)

        # Checkpoint 2 : premier virage à droite
        for col_idx in range(11, 14):
            grid[3][col_idx].block = Checkpoint(2)

        # Checkpoint 3 : partie inférieure du circuit
        for row_idx in range(7, 9):
            grid[row_idx][11].block = Checkpoint(3)

        # Checkpoint 4 : retour sur le côté gauche
        for col_idx in range(1, 4):
            grid[7][col_idx].block = Checkpoint(4)

        # Ligne d'arrivée et positions de départ
        # Ligne d'arrivée sur la partie supérieure
        for row_idx in range(1, 3):
            grid[row_idx][4].block = FinishLine()

        # Position de départ du joueur 1
        grid[1][2].block = StartBlock(1)

        # Position de départ du joueur 2
        grid[2][2].block = StartBlock(2)

        # Boosts : accélération temporaire des voitures
        # Boost 1 : première partie du circuit
        grid[2][6].block = Boost()

        # Boost 2 : virage central
        grid[5][11].block = Boost()

        # Boost 3 : partie inférieure
        grid[10][10].block = Boost()

        # 6. INITIALISATION DU CIRCUIT ET DES VOITURES
        # Enregistrer la grille dans un objet Circuit
        self.circuit = Circuit(
            grid=grid,
            name="Circuit 3"
        )

        # Positionner les deux voitures sur leurs cases de départ
        self.spawn_car()


    def start_race(self, circuit_index: int) -> None:
        """Sélectionne un circuit et démarre une nouvelle course."""
        self.selected_index = circuit_index

        if circuit_index == 0:
            self.load_circuit()

        elif circuit_index == 1:
            self.load_second_circuit()

        elif circuit_index == 2:
            self.load_third_circuit()

        else:
            raise ValueError("Indice de circuit invalide")

        self.race = Race()
        self.last_blocks = [None, None]
        self.state = GameState.RACING

    def spawn_car(self) -> None:
        """
        Crée les deux voitures sur leurs positions de départ.

        Cette méthode recherche les blocs StartBlock des joueurs
        1 et 2 dans la grille du circuit sélectionné.

        Pour chaque joueur, elle calcule le centre de sa case de
        départ, crée un objet Car et mémorise sa position initiale
        pour permettre une réapparition en cas de chute.

        Les voitures sont rangées dans self.cars :
        - Indice 0 : voiture du joueur 1.
        - Indice 1 : voiture du joueur 2.

        Retour
        ------
        None
            Les voitures et leurs positions de départ sont
            enregistrées directement dans le modèle.
        """

        # Vérifier qu'un circuit est chargé
        if self.circuit is None:
            return

        # Réinitialiser les voitures et leurs positions de départ
        self.cars = []
        self.last_checkpoint_positions = [None, None]

        # Créer successivement les voitures des joueurs 1 et 2
        for player in (1, 2):
            start_tile = None

            # Rechercher la case de départ du joueur
            for row in self.circuit.grid:
                for tile in row:
                    if (isinstance(tile.block, StartBlock)
                            and tile.block.letter == str(player)):
                        start_tile = tile

            # Vérifier qu'une position de départ a été trouvée
            if start_tile is None:
                raise ValueError("Départ du joueur introuvable")

            # Calculer les coordonnées du centre de la case
            x = (start_tile.col + 0.5) * TILE_SIZE
            y = (start_tile.row + 0.5) * TILE_SIZE

            # Créer la voiture et l'ajouter à la liste
            self.cars.append(Car(player, x, y))

            # Mémoriser la position initiale de réapparition
            self.last_checkpoint_positions[player - 1] = (x, y)

        # Conserver l'ancienne référence pour le contrôleur et la vue
        self.car = self.cars[0]

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

                # Réapparition de la voiture au dernier checkpoint validé
                # La méthode respawn remet aussi la vitesse et les effets à zéro
                car.respawn(position[0], position[1])

                # Réinitialiser la détection des blocs spéciaux
                self.last_blocks[index] = None
    def update(self, dt: float = 1 / FPS) -> None:
        """
        Met à jour les voitures et les événements de la course.

        Cette méthode est exécutée lorsque la course est active.
        Elle parcourt les voitures des deux joueurs et récupère
        le terrain situé sous chacune d'elles.

        Pour chaque voiture, elle actualise son déplacement en
        tenant compte des propriétés du terrain, vérifie si elle
        est tombée dans le vide, puis détecte les éventuels blocs
        spéciaux : checkpoints, boosts et ligne d'arrivée.

        Paramètres
        ----------
        dt : float
            Durée écoulée entre deux mises à jour, en secondes.
            Par défaut, cette durée correspond à 1 / FPS.

        Retour
        ------
        None
            Les positions des voitures et les données de la
            course sont directement mises à jour.
        """

        # Vérifier que la course est active et qu'un circuit existe
        if self.state != GameState.RACING or self.circuit is None:
            return

        # Parcourir les voitures des deux joueurs
        for car in self.cars:

            # Récupérer le terrain sous la voiture
            tile = self.circuit.get_tile_at_pixel(car.x, car.y)

            # Actualiser le déplacement si le terrain est praticable
            if tile is not None and not tile.terrain.is_void:
                car.update(dt, tile.terrain)

            # Vérifier une chute et réapparaître si nécessaire
            self.check_car_void(car, car.player)

            # Détecter les checkpoints, les boosts et l'arrivée
            self.check_car_block(car, car.player)
