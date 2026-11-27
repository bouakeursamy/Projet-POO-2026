"""Voiture d'un joueur : position, vitesse et dynamique."""

import math
from constants import (
    CAR_ACCELERATION, CAR_BRAKE, CAR_REVERSE_ACCELERATION,
    AIR_DRAG, ROLLING_RESISTANCE, CAR_WHEELBASE, CAR_MAX_STEERING,
    CAR_STEERING_SPEED, BOOST_ACCELERATION, BOOST_DURATION
)
from model.terrain import Terrain


class Car:
    """Voiture pilotée par un joueur (modèle équilibré par défaut).

    Parameters
    ----------
    player : int
        Numéro du joueur (1 ou 2).
    x : float
        Position de départ en x, en pixels.
    y : float
        Position de départ en y, en pixels.
    name : str
        Nom du modèle, affiché dans le menu.
    acceleration : float
        Accélération du moteur, en pixels par seconde au carré.
    max_steering : float
        Braquage maximal des roues avant, en radians.
    air_drag : float
        Frottement de l'air : plus il est petit, plus la voiture va vite.
    """

    def __init__(self, player: int, x: float, y: float,
                 name: str = "Équilibrée",
                 acceleration: float = CAR_ACCELERATION,
                 max_steering: float = CAR_MAX_STEERING,
                 air_drag: float = AIR_DRAG):
        self.player = player
        self.name = name
        self.acceleration = acceleration
        self.max_steering = max_steering
        self.air_drag = air_drag
        self.x = x
        self.y = y
        # vitesse en pixels par seconde, découpée selon les axes x et y
        self.vx: float = 0.0
        self.vy: float = 0.0
        # orientation en radians : 0 vers la droite, positif vers la gauche
        self.angle: float = 0.0
        # angle des roues avant, en radians
        self.steering: float = 0.0
        self.drifting: bool = False
        self.boost_time: float = 0.0
        # commandes de la frame en cours, remises à 0 à la fin de update
        self.throttle: int = 0
        self.steer_command: int = 0

    def accelerate(self) -> None:
        """Demande d'accélérer pendant cette frame."""
        self.throttle = 1

    def brake(self) -> None:
        """Demande de freiner, ou de reculer si la voiture est arrêtée."""
        self.throttle = -1

    def turn_left(self) -> None:
        """Demande de tourner à gauche pendant cette frame."""
        self.steer_command = 1

    def turn_right(self) -> None:
        """Demande de tourner à droite pendant cette frame."""
        self.steer_command = -1

    def boost(self) -> None:
        """Active le boost de la voiture pendant BOOST_DURATION secondes."""
        self.boost_time = BOOST_DURATION

    def respawn(self, x: float, y: float) -> None:
        """Replace la voiture à l'arrêt, par exemple après une chute.

        Parameters
        ----------
        x : float
            Nouvelle position en x, en pixels.
        y : float
            Nouvelle position en y, en pixels.
        """
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        # on efface aussi tout ce qui pourrait relancer la voiture
        self.steering = 0.0
        self.drifting = False
        self.boost_time = 0.0

    def update(self, dt: float, terrain: Terrain) -> None:
        """Fait avancer et tourner la voiture pendant une frame.

        Parameters
        ----------
        dt : float
            Durée de la frame, en secondes.
        terrain : Terrain
            Terrain de la case où se trouve la voiture.
        """
        self._update_steering(dt)

        # vecteur vers l'avant de la voiture ; l'axe y de pygame descend,
        # d'où le signe moins devant le sinus
        forward_x = math.cos(self.angle)
        forward_y = -math.sin(self.angle)
        # vitesse dans l'axe de la voiture, négative en marche arrière
        speed = self.vx * forward_x + self.vy * forward_y

        # modèle bicyclette : plus on roule vite, plus on tourne vite ;
        # en marche arrière (speed < 0), le virage s'inverse tout seul
        self.angle += speed / CAR_WHEELBASE * math.tan(self.steering) * dt

        # axes de la voiture après le virage ; l'axe y de pygame descend
        forward_x = math.cos(self.angle)
        forward_y = -math.sin(self.angle)
        left_x = -math.sin(self.angle)
        left_y = -math.cos(self.angle)
        # le nez a tourné mais pas la vitesse : une partie part de côté
        speed = self.vx * forward_x + self.vy * forward_y
        side_speed = self.vx * left_x + self.vy * left_y

        speed = self._apply_engine(speed, dt, terrain.traction)
        side_speed = self._apply_grip(side_speed, dt, terrain)
        if self.boost_time > 0:
            self.boost_time -= dt

        self.vx = speed * forward_x + side_speed * left_x
        self.vy = speed * forward_y + side_speed * left_y
        self.x += self.vx * dt
        self.y += self.vy * dt

        self.throttle = 0
        self.steer_command = 0

    def _update_steering(self, dt: float) -> None:
        """Tourne les roues avant vers la position demandée par le joueur.

        Parameters
        ----------
        dt : float
            Durée de la frame, en secondes.
        """
        target = self.steer_command * self.max_steering
        step = CAR_STEERING_SPEED * dt
        # les roues tournent peu à peu, sans dépasser la cible
        if self.steering < target:
            self.steering = min(self.steering + step, target)
        elif self.steering > target:
            self.steering = max(self.steering - step, target)

    def _apply_grip(self, side_speed: float, dt: float,
                    terrain: Terrain) -> float:
        """Annule ou freine le glissement de côté selon le terrain.

        Parameters
        ----------
        side_speed : float
            Vitesse de côté de la voiture, en pixels par seconde.
        dt : float
            Durée de la frame, en secondes.
        terrain : Terrain
            Terrain de la case où se trouve la voiture.

        Returns
        -------
        float
            La nouvelle vitesse de côté.
        """
        # effort que les pneus devraient fournir pour annuler le
        # glissement en une frame ; dans un virage, il vaut v² / rayon
        needed = abs(side_speed) / dt
        if needed <= terrain.drift_threshold:
            # les pneus tiennent : la voiture va là où elle pointe
            self.drifting = False
            return 0.0
        # les pneus lâchent : le glissement diminue seulement un peu
        self.drifting = True
        reduction = terrain.drift_friction * dt
        if side_speed > 0:
            return max(side_speed - reduction, 0.0)
        return min(side_speed + reduction, 0.0)

    def _apply_engine(self, speed: float, dt: float,
                      traction: float) -> float:
        """Applique le moteur, les freins et les frottements à la vitesse.

        Parameters
        ----------
        speed : float
            Vitesse dans l'axe de la voiture, en pixels par seconde.
        dt : float
            Durée de la frame, en secondes.
        traction : float
            Adhérence du terrain, entre 0 et 1.

        Returns
        -------
        float
            La nouvelle vitesse dans l'axe de la voiture.
        """
        # un terrain glissant transmet moins la force du moteur et des freins
        if self.throttle == 1:
            speed += self.acceleration * traction * dt
        elif self.throttle == -1:
            # on freine si on avance, sinon on recule
            if speed > 0:
                speed -= CAR_BRAKE * traction * dt
            else:
                speed -= CAR_REVERSE_ACCELERATION * traction * dt

        # le boost pousse la voiture vers l'avant tant qu'il dure
        if self.boost_time > 0:
            speed += BOOST_ACCELERATION * dt

        # l'air freine plus fort à grande vitesse : c'est lui qui fixe
        # la vitesse maximale ; le roulement arrête une voiture en roue libre
        speed -= self.air_drag * speed * abs(speed) * dt
        speed -= ROLLING_RESISTANCE * speed * dt
        return speed

    def get_speed(self) -> float:
        """Renvoie la vitesse de la voiture, en pixels par seconde."""
        return math.sqrt(self.vx ** 2 + self.vy ** 2)


class SportCar(Car):
    """Voiture rapide : forte accélération, mais braque moins."""

    def __init__(self, player: int, x: float, y: float):
        super().__init__(player, x, y, "Rapide", 360.0, 0.26, 0.0022)


class AgileCar(Car):
    """Voiture agile : tourne plus serré, mais va moins vite."""

    def __init__(self, player: int, x: float, y: float):
        super().__init__(player, x, y, "Agile", 270.0, 0.42, 0.0034)
