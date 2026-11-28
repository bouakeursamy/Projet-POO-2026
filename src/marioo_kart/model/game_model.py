
import math

from constants import (
    GameState, GRID_ROWS, GRID_COLS, TILE_SIZE, FPS,
    BOOST_DURATION, CAR_WIDTH, CAR_HEIGHT
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
                border = (
                    row_idx <= 3 or row_idx >= 8
                    or col_idx <= 3 or col_idx >= 12
                )

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
                if 5 <= row_idx <= 6 and 6 <= col_idx <= 9:
                    terrain = Void()

                # Ajouter un trou sur la route à droite du circuit
                if row_idx == 7 and col_idx == 12:
                    terrain = Void()

                # Placer quatre murs aux coins de la zone d'herbe
                if row_idx in (4, 7) and col_idx in (4, 11):
                    terrain = Wall()

                tile = RoadTile(col_idx, row_idx, terrain)
                row.append(tile)

            grid.append(row)

        # Checkpoints du premier circuit
        for row_idx in range(1, 4):
            grid[row_idx][10].block = Checkpoint(1)

        for col_idx in range(12, 15):
            grid[5][col_idx].block = Checkpoint(2)

        for row_idx in range(8, 11):
            grid[row_idx][9].block = Checkpoint(3)

        for col_idx in range(1, 4):
            grid[6][col_idx].block = Checkpoint(4)

        # Ligne d'arrivée
        for row_idx in range(1, 4):
            grid[row_idx][4].block = FinishLine()

        # Départs et boosts
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

                if (
                    top or left or middle_left or inner
                    or bottom or right or middle or upper
                ):
                    terrain = Road()
                else:
                    terrain = Grass()

                # Terrains particuliers
                if 1 <= row_idx <= 3 and 5 <= col_idx <= 7:
                    terrain = Ice()
                elif 8 <= row_idx <= 10 and 8 <= col_idx <= 10:
                    terrain = Dirt()
                elif row_idx in (0, 11) or col_idx in (0, 15):
                    terrain = Void()

                # Trois cases de vide au centre du circuit
                if row_idx == 7 and 9 <= col_idx <= 11:
                    terrain = Void()

                # Trou sur la route du bas
                if row_idx == 8 and col_idx == 11:
                    terrain = Void()

                # Murs sur le contour intérieur de la zone d'herbe
                if row_idx == 4 and 4 <= col_idx <= 7:
                    terrain = Wall()

                if 5 <= row_idx <= 7 and col_idx == 7:
                    terrain = Wall()

                if row_idx == 7 and col_idx == 8:
                    terrain = Wall()

                row.append(RoadTile(col_idx, row_idx, terrain))

            grid.append(row)

        # Checkpoints
        for row_idx in range(1, 4):
            grid[row_idx][8].block = Checkpoint(1)

        for col_idx in range(12, 15):
            grid[6][col_idx].block = Checkpoint(2)

        for row_idx in range(8, 11):
            grid[row_idx][8].block = Checkpoint(3)

        for col_idx in range(1, 4):
            grid[5][col_idx].block = Checkpoint(4)

        # Ligne d'arrivée
        for row_idx in range(1, 4):
            grid[row_idx][4].block = FinishLine()

        # Départs
        grid[2][2].block = StartBlock(1)
        grid[3][2].block = StartBlock(2)

        # Boosts
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

        for row_idx in range(GRID_ROWS):
            row = []

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

                # Route sur le tracé, murs sur les autres cases
                if is_road:
                    terrain = Road()
                else:
                    terrain = Wall()

                # ==================================================
                # 2. BORDURES ET TERRAINS PARTICULIERS
                # ==================================================

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

                # ==================================================
                # 3. OBSTACLES ET ZONES DANGEREUSES
                # ==================================================

                # Trous à éviter pendant la course
                if (row_idx, col_idx) in (
                    (2, 8),
                    (4, 10),
                    (7, 10),
                ):
                    terrain = Void()

                # Murs dans la partie supérieure
                if row_idx == 3 and 5 <= col_idx <= 8:
                    terrain = Wall()

                # Murs dans la partie centrale
                if row_idx == 6 and 10 <= col_idx <= 12:
                    terrain = Wall()

                # Murs dans la partie inférieure
                if row_idx == 8 and 5 <= col_idx <= 7:
                    terrain = Wall()

                # ==================================================
                # 4. PERSONNALISATION DU CIRCUIT
                # ==================================================

                # Bande d'herbe à droite
                if col_idx == 14 and 1 <= row_idx <= 7:
                    terrain = Grass()

                # Mur remplaçant l'ancien trou dans la terre
                if row_idx == 9 and col_idx == 7:
                    terrain = Wall()

                # Murs sur une partie de la dernière ligne
                if row_idx == 11 and 6 <= col_idx <= 10:
                    terrain = Wall()

                # Créer la case avec son terrain définitif
                tile = RoadTile(col_idx, row_idx, terrain)
                row.append(tile)

            grid.append(row)

        # ==========================================================
        # 5. PLACEMENT DES BLOCS SPÉCIAUX
        # ==========================================================

        # Checkpoint 1 : partie supérieure
        for row_idx in range(1, 3):
            grid[row_idx][7].block = Checkpoint(1)

        # Checkpoint 2 : premier virage à droite
        for col_idx in range(11, 14):
            grid[3][col_idx].block = Checkpoint(2)

        # Checkpoint 3 : partie inférieure
        for row_idx in range(7, 9):
            grid[row_idx][11].block = Checkpoint(3)

        # Checkpoint 4 : retour à gauche
        for col_idx in range(1, 4):
            grid[7][col_idx].block = Checkpoint(4)

        # Ligne d'arrivée
        for row_idx in range(1, 3):
            grid[row_idx][4].block = FinishLine()

        # Départs des joueurs
        grid[1][2].block = StartBlock(1)
        grid[2][2].block = StartBlock(2)

        # Trois boosts
        grid[2][6].block = Boost()
        grid[5][11].block = Boost()
        grid[10][10].block = Boost()

        # ==========================================================
        # 6. INITIALISATION DU CIRCUIT ET DES VOITURES
        # ==========================================================

        self.circuit = Circuit(
            grid=grid,
            name="Circuit 3"
        )
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

        # Créer les voitures des deux joueurs
        for player in (1, 2):
            start_tile = None

            # Rechercher la case de départ du joueur
            for row in self.circuit.grid:
                for tile in row:
                    if (
                        isinstance(tile.block, StartBlock)
                        and tile.block.letter == str(player)
                    ):
                        start_tile = tile

            if start_tile is None:
                raise ValueError("Départ du joueur introuvable")

            # Calculer le centre de la case de départ
            x = (start_tile.col + 0.5) * TILE_SIZE
            y = (start_tile.row + 0.5) * TILE_SIZE

            self.cars.append(Car(player, x, y))
            self.last_checkpoint_positions[player - 1] = (x, y)

        # Référence conservée pour le contrôleur et la vue
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
            block_id = "B"
        else:
            self.last_blocks[index] = None
            return

        if block_id == self.last_blocks[index]:
            return

        self.last_blocks[index] = block_id

        if isinstance(block, Checkpoint):
            # Sauvegarder le nombre de checkpoints validés
            previous_count = self.race.checkpoints[index]

            # Vérifier si le checkpoint est dans le bon ordre
            self.race.pass_checkpoint(player, block.number)

            # Mémoriser la position si le checkpoint est validé
            if self.race.checkpoints[index] > previous_count:
                self.last_checkpoint_positions[index] = (
                    (tile.col + 0.5) * TILE_SIZE,
                    (tile.row + 0.5) * TILE_SIZE
                )

        elif isinstance(block, FinishLine):
            self.race.pass_finish_line(player)

        elif isinstance(block, Boost):
            car.boost_time = BOOST_DURATION

    def check_car_wall(
        self,
        car: Car,
        previous_x: float,
        previous_y: float
    ) -> None:
        """
        Empêche une voiture de traverser les murs en briques.

        Calcule les quatre coins de la carrosserie orientée,
        puis vérifie son déplacement par petites étapes.
        En cas de collision, la voiture s'arrête à la dernière
        position autorisée, sans être téléportée.
        """
        if self.circuit is None:
            return

        # Dimensions de la voiture
        demi_longueur = CAR_HEIGHT / 2
        demi_largeur = CAR_WIDTH / 2

        # Axes de la voiture selon son orientation
        avant_x = math.cos(car.angle)
        avant_y = -math.sin(car.angle)

        cote_x = math.sin(car.angle)
        cote_y = math.cos(car.angle)

        def touche_un_mur(x: float, y: float) -> bool:
            """Vérifie si la carrosserie touche un terrain solide."""

            # Calculer les quatre coins de la voiture tournée
            coins_voiture = []

            for sens_longueur in (-1, 1):
                for sens_largeur in (-1, 1):
                    coin_x = (
                        x
                        + sens_longueur * demi_longueur * avant_x
                        + sens_largeur * demi_largeur * cote_x
                    )
                    coin_y = (
                        y
                        + sens_longueur * demi_longueur * avant_y
                        + sens_largeur * demi_largeur * cote_y
                    )
                    coins_voiture.append((coin_x, coin_y))

            # Déterminer les cases proches de la voiture
            col_min = int(min(p[0] for p in coins_voiture) // TILE_SIZE)
            col_max = int(max(p[0] for p in coins_voiture) // TILE_SIZE)
            row_min = int(min(p[1] for p in coins_voiture) // TILE_SIZE)
            row_max = int(max(p[1] for p in coins_voiture) // TILE_SIZE)

            # Examiner les cases voisines
            for row_idx in range(row_min, row_max + 1):
                for col_idx in range(col_min, col_max + 1):

                    tile = self.circuit.get_tile(col_idx, row_idx)

                    if tile is None or not tile.terrain.is_solid:
                        continue

                    # Limites du mur
                    gauche = col_idx * TILE_SIZE
                    droite = gauche + TILE_SIZE
                    haut = row_idx * TILE_SIZE
                    bas = haut + TILE_SIZE

                    coins_mur = [
                        (gauche, haut),
                        (droite, haut),
                        (droite, bas),
                        (gauche, bas),
                    ]

                    # Axes de projection des rectangles
                    axes = [
                        (1.0, 0.0),
                        (0.0, 1.0),
                        (avant_x, avant_y),
                        (cote_x, cote_y),
                    ]

                    collision = True

                    for axe_x, axe_y in axes:
                        projections_voiture = [
                            px * axe_x + py * axe_y
                            for px, py in coins_voiture
                        ]
                        projections_mur = [
                            px * axe_x + py * axe_y
                            for px, py in coins_mur
                        ]

                        # Vérifier si les projections se séparent
                        if (
                            max(projections_voiture) <= min(projections_mur)
                            or max(projections_mur) <= min(projections_voiture)
                        ):
                            collision = False
                            break

                    if collision:
                        return True

            return False
        # Vérifier si la position précédente est déjà en collision
        if touche_un_mur(previous_x, previous_y):

            # Chercher progressivement une position libre à proximité
            for distance in range(1, 2 * TILE_SIZE + 1):

                # Essayer les quatre directions autour de la voiture
                positions_possibles = [
                    (previous_x + distance, previous_y),
                    (previous_x - distance, previous_y),
                    (previous_x, previous_y + distance),
                    (previous_x, previous_y - distance),
                ]

                for x, y in positions_possibles:

                    # Vérifier que la case existe et est praticable
                    tile = self.circuit.get_tile_at_pixel(x, y)

                    if (
                        tile is None
                        or tile.terrain.is_void
                        or tile.terrain.is_solid
                    ):
                        continue

                    # Vérifier que toute la carrosserie est dégagée
                    if not touche_un_mur(x, y):

                        # Replacer la voiture juste hors du mur
                        car.x = x
                        car.y = y

                        # Annuler la vitesse après le dégagement
                        car.vx = 0.0
                        car.vy = 0.0

                        return

            # Si aucune position libre n'est trouvée,
            # éviter de conserver le déplacement dangereux
            car.x = previous_x
            car.y = previous_y
            car.vx = 0.0
            car.vy = 0.0
            return

        # Destination calculée par Car.update()
        destination_x = car.x
        destination_y = car.y

        dx = destination_x - previous_x
        dy = destination_y - previous_y

        # Découper le déplacement en étapes de 2 pixels
        distance = math.hypot(dx, dy)
        nombre_etapes = max(1, math.ceil(distance / 2.0))

        derniere_position_x = previous_x
        derniere_position_y = previous_y

        for etape in range(1, nombre_etapes + 1):
            progression = etape / nombre_etapes

            position_x = previous_x + progression * dx
            position_y = previous_y + progression * dy

            # Arrêter la voiture dès le premier contact
            if touche_un_mur(position_x, position_y):

                # Revenir à la dernière position sans collision
                car.x = derniere_position_x
                car.y = derniere_position_y

                # Annuler la vitesse
                car.vx = 0.0
                car.vy = 0.0
                return

            # Conserver la dernière position autorisée
            derniere_position_x = position_x
            derniere_position_y = position_y

    def check_car_void(self, car: Car, player: int) -> None:
        """
        Vérifie si une voiture est tombée dans une zone de vide.

        En cas de chute, la voiture réapparaît à son dernier
        checkpoint validé, ou à son point de départ.
        """
        if self.circuit is None:
            return

        tile = self.circuit.get_tile_at_pixel(car.x, car.y)

        if tile is None or tile.terrain.is_void:
            index = player - 1
            position = self.last_checkpoint_positions[index]

            if position is not None:
                car.respawn(position[0], position[1])
                self.last_blocks[index] = None

    def update(self, dt: float = 1 / FPS) -> None:
        """
        Met à jour les voitures pendant la course.

        Gère les déplacements, les collisions avec les murs,
        les chutes dans le vide et les blocs spéciaux.
        """
        if self.state != GameState.RACING or self.circuit is None:
            return

        # Mettre à jour les deux voitures
        for car in self.cars:

            # Conserver la position avant le déplacement
            previous_x = car.x
            previous_y = car.y

            # Récupérer le terrain sous la voiture
            tile = self.circuit.get_tile_at_pixel(car.x, car.y)

            # Déplacer la voiture uniquement sur un terrain praticable
            # Vérifier que la voiture n'est pas dans le vide
            if tile is not None and not tile.terrain.is_void:

                # Déplacer la voiture si son centre est hors d'un mur
                if not tile.terrain.is_solid:
                    car.update(dt, tile.terrain)

                # Vérifier les collisions même si la voiture
                # est déjà coincée dans une case de mur
                self.check_car_wall(car, previous_x, previous_y)

            # Gérer les chutes
            self.check_car_void(car, car.player)

            # Vérifier checkpoints, boosts et ligne d'arrivée
            self.check_car_block(car, car.player)
