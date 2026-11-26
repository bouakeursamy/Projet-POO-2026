# Projet POO 2026 — Jeu de course 2D

Jeu de course de voitures en 2D pour deux joueurs sur un seul clavier,
inspiré de Mario Kart et de Trackmania. Projet de programmation orientée
objet en Python (Sorbonne Université, 2026), réalisé par Sofiane Ikhlef,
Samy Bouakeur et Ahcene Nahi.

## Installation

Il faut Python 3.10 ou plus récent, et Git.

```
git clone https://github.com/bouakeursamy/Projet-POO-2026.git
cd Projet-POO-2026
pip install virtualenv
virtualenv venv
source venv/bin/activate        # Linux et macOS
source venv/Scripts/activate    # Windows (Git Bash)
pip install -r requirements.txt
```

Sur Linux, si `pip install virtualenv` est refusé, installer plutôt le
paquet du système : `sudo apt install python3-virtualenv`.

## Lancer le jeu

```
python src/marioo_kart/main.py
```

## Commandes

| Action              | Joueur 1 (voiture rouge) | Joueur 2 (voiture bleue) |
| ------------------- | ------------------------ | ------------------------ |
| Accélérer           | Z ou W                   | Flèche du haut           |
| Freiner / reculer   | S                        | Flèche du bas            |
| Tourner à gauche    | Q ou A                   | Flèche gauche            |
| Tourner à droite    | D                        | Flèche droite            |

Les deux lettres (Z et W, Q et A) permettent de jouer en AZERTY comme en
QWERTY.

Menus :

- menu principal : Entrée pour jouer, Échap pour quitter ;
- choix du circuit : flèches du haut et du bas, Entrée pour lancer la
  course, Échap pour revenir au menu ;
- pendant la course : Échap pour revenir au menu ;
- fin de course : Entrée ou Échap pour revenir au menu.

## Règles du jeu

- Une course se joue en 3 tours. Le premier joueur qui termine ses 3 tours
  gagne.
- Un tour compte seulement si la voiture passe les 4 points de passage dans
  l'ordre, puis la ligne d'arrivée.
- Les terrains changent le comportement de la voiture :
  - route : bonne traction, la voiture dérape seulement à grande vitesse
    dans un virage serré ;
  - herbe : la voiture accélère moins bien et dérape plus facilement ;
  - terre : encore moins de traction, la voiture dérape très facilement ;
  - glace : très peu de traction, la voiture glisse presque tout le temps ;
  - vide : la voiture revient à son dernier point de passage, à l'arrêt.
    Sortir de la carte compte comme tomber dans le vide.
- Les cases de boost (B) donnent une poussée pendant une seconde.
- Le dérapage est automatique : il commence quand un virage demande plus
  d'adhérence que le terrain ne peut en donner.

## Organisation du code

Le code suit le patron MVC, dans `src/marioo_kart/` :

- `model/` : les données et les règles du jeu, sans affichage ni clavier.
  - `car.py` : la voiture et sa physique (accélération, freinage,
    direction, dérapage, boost) ;
  - `terrain.py` : les cinq terrains et leurs propriétés ;
  - `road_tile.py`, `circuit.py` : les cases et le circuit ;
  - `start_block.py`, `checkpoint.py`, `finish_line.py`, `boost.py` : les
    blocs posés sur les cases ;
  - `race.py` : les tours, les points de passage et le vainqueur ;
  - `game_model.py` : l'état du jeu, les circuits et la mise à jour des
    voitures.
- `view/game_view.py` : l'affichage avec pygame (menus, circuit, voitures).
- `controller/` : la boucle de jeu (`game_controller.py`) et la lecture du
  clavier (`input_handler.py`).
- `constants.py` : les réglages (taille de la fenêtre, constantes de la
  voiture, couleurs).


