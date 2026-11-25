"""Voiture d'un joueur : position, vitesse et image."""

import pygame
import math
from constants import (
    CAR_ACCELERATION, CAR_BRAKE, CAR_REVERSE_ACCELERATION,
    AIR_DRAG, ROLLING_RESISTANCE, CAR_WHEELBASE, CAR_MAX_STEERING,
    BOOST_ACCELERATION, BOOST_DURATION, CAR_WIDTH, CAR_HEIGHT
)
from model.terrain import Terrain


class Car:
    """Voiture pilotée par un joueur.

    Parameters
    ----------
    player : int
        Numéro du joueur (1 ou 2).
    x : float
        Position de départ en x, en pixels.
    y : float
        Position de départ en y, en pixels.
    """

    def __init__(self, player: int, x: float, y: float):
        self.player = player
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
        self.sprite = self.build_sprite()

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
        # les roues avant sont soit droites, soit braquées au maximum
        self.steering = self.steer_command * CAR_MAX_STEERING

        # vecteur vers l'avant de la voiture ; l'axe y de pygame descend,
        # d'où le signe moins devant le sinus
        forward_x = math.cos(self.angle)
        forward_y = -math.sin(self.angle)
        # vitesse dans l'axe de la voiture, négative en marche arrière
        speed = self.vx * forward_x + self.vy * forward_y

        # modèle bicyclette : plus on roule vite, plus on tourne vite ;
        # en marche arrière (speed < 0), le virage s'inverse tout seul
        self.angle += speed / CAR_WHEELBASE * math.tan(self.steering) * dt

        speed = self._apply_engine(speed, dt, terrain.traction)
        if self.boost_time > 0:
            self.boost_time -= dt

        # pour l'instant la voiture adhère toujours : la vitesse suit le nez
        forward_x = math.cos(self.angle)
        forward_y = -math.sin(self.angle)
        self.vx = speed * forward_x
        self.vy = speed * forward_y
        self.x += self.vx * dt
        self.y += self.vy * dt

        self.throttle = 0
        self.steer_command = 0

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
            speed += CAR_ACCELERATION * traction * dt
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
        speed -= AIR_DRAG * speed * abs(speed) * dt
        speed -= ROLLING_RESISTANCE * speed * dt
        return speed

    def get_speed(self) -> float:
        """Renvoie la vitesse de la voiture, en pixels par seconde."""
        return math.sqrt(self.vx ** 2 + self.vy ** 2)

    def build_sprite(self) -> pygame.Surface:
        """Crée l'image de la voiture : un rectangle rouge qui pointe à droite.

        Returns
        -------
        pygame.Surface
            Image de la voiture, sur un fond transparent.
        """
        # SRCALPHA garde le fond transparent autour du rectangle
        # la longueur est en x, car l'angle 0 regarde vers la droite
        surf = pygame.Surface((CAR_HEIGHT, CAR_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 0, 0), (0, 0, CAR_HEIGHT,
                         CAR_WIDTH), border_radius=5)
        return surf

    def get_rotated_sprite(self) -> tuple[pygame.Surface, pygame.Rect]:
        """Renvoie l'image tournée selon l'angle, et sa place à l'écran.

        Returns
        -------
        tuple[pygame.Surface, pygame.Rect]
            L'image tournée et le rectangle centré sur la voiture.
        """
        # pygame veut des degrés et tourne dans le sens trigonométrique,
        # comme notre angle
        rotated = pygame.transform.rotate(self.sprite,
                                          math.degrees(self.angle))
        # l'image tournée est plus grande : on la recentre sur la voiture
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        return rotated, rect
