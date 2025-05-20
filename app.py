import pyxel

# --- PARAMÈTRES GÉNÉRAUX ---
SCREEN_SIZE = 512                  # Taille totale de l'écran
ZONE_SIZE = SCREEN_SIZE // 2       # Taille d'un quart de zone
PLAYER_SIZE = 16                   # Taille d'un ninja
BALL_WIDTH = 14                    # Largeur des shurikens
BALL_HEIGHT = 14                   # Hauteur des shurikens
SPAWN_INTERVAL = 60                # 1 seconde à 60 FPS
PLAYER_SPEED = 4                   # Vitesse de déplacement du joueur

# --- PARAMÈTRES DE DIFFICULTÉ ---
SHURIKEN_SPEED_FACTOR = 60         # Plus petit = shuriken plus rapide
ANIM_SPEED = 5                     # Plus petit = shuriken tourne plus vite

# --- CONTRÔLES PAR JOUEUR ---
CONTROLS = [
    {   # Joueur 1
        'up': pyxel.KEY_S,      # haut   : S
        'down': pyxel.KEY_D,    # bas    : D
        'left': pyxel.KEY_F,    # gauche : F
        'right': pyxel.KEY_G,   # droite : G
    },
    {   # Joueur 2
        'up': pyxel.KEY_H,      # haut   : H
        'down': pyxel.KEY_J,    # bas    : J
        'left': pyxel.KEY_K,    # gauche : K
        'right': pyxel.KEY_L,   # droite : L
    },
    {   # Joueur 3
        'up': pyxel.KEY_C,      # haut   : C
        'down': pyxel.KEY_V,    # bas    : V
        'left': pyxel.KEY_B,    # gauche : B
        'right': pyxel.KEY_N,   # droite : N
    },
    {   # Joueur 4 (flèches)
        'up': pyxel.KEY_UP,         # haut   : ↑
        'down': pyxel.KEY_DOWN,     # bas    : ↓
        'left': pyxel.KEY_LEFT,     # gauche : ←
        'right': pyxel.KEY_RIGHT,   # droite : →
    }
]

# --- COINS D'APPARITION RELATIFS DANS UNE ZONE ---
RELATIVE_CORNERS = [
    (0, 0),
    (ZONE_SIZE - 1, 0),
    (0, ZONE_SIZE - 1),
    (ZONE_SIZE - 1, ZONE_SIZE - 1)
]

# --- CLASSE JOUEUR ---
class Player:
    def __init__(self, index):
        self.index = index
        self.x = ZONE_SIZE // 2
        self.y = ZONE_SIZE // 2
        self.alive = True

    def move(self, keys):
        # Déplacement basé sur les touches
        if pyxel.btn(keys['up']):
            self.y = max(0, self.y - PLAYER_SPEED)
        if pyxel.btn(keys['down']):
            self.y = min(ZONE_SIZE - PLAYER_SIZE, self.y + PLAYER_SPEED)
        if pyxel.btn(keys['left']):
            self.x = max(0, self.x - PLAYER_SPEED)
        if pyxel.btn(keys['right']):
            self.x = min(ZONE_SIZE - PLAYER_SIZE, self.x + PLAYER_SPEED)

    def draw(self, ox, oy):
        if self.alive:
            # Coordonnées dans la feuille de sprites pour le ninja
            u = 16 * (self.index % 2)
            v = 16 * (self.index // 2)
            pyxel.blt(ox + self.x, oy + self.y, 0, u, v, 16, 16, 1)

# --- CLASSE SHURIKEN ---
class Ball:
    def __init__(self, x, y, dx, dy, bounds):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.bounds = bounds  # Limites du quart de zone
        self.anim_frame = 0   # Frame d’animation
        self.active = True    # Sert à désactiver le shuriken s’il sort

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.anim_frame = (self.anim_frame + 1) % (2 * ANIM_SPEED)

        # Supprimer le shuriken s’il sort de son quart
        x_min, y_min, x_max, y_max = self.bounds
        if not (x_min <= self.x <= x_max and y_min <= self.y <= y_max):
            self.active = False

    def draw(self):
        # Animation simple à 2 images
        u = 0 if self.anim_frame < ANIM_SPEED else 16
        v = 32
        pyxel.blt(int(self.x - 1), int(self.y - 1), 0, u, v, BALL_WIDTH, BALL_HEIGHT, 1)

# --- CLASSE MINI-JEU PAR QUART ---
class MiniGame:
    def __init__(self, index):
        self.index = index
        self.origin_x = (index % 2) * ZONE_SIZE
        self.origin_y = (index // 2) * ZONE_SIZE
        self.controls = CONTROLS[index]
        self.reset()

    def reset(self):
        self.player = Player(self.index)
        self.balls = []
        self.frames = 0
        self.lost = False

    def update(self):
        if not self.player.alive:
            self.lost = True
            return

        self.frames += 1
        self.player.move(self.controls)

        if not self.lost:
            # Envoie un shuriken toutes les 15 frames, alternant les coins
            if self.frames % (SPAWN_INTERVAL // 4) == 0:
                corner_index = (self.frames // (SPAWN_INTERVAL // 4)) % 4
                cx, cy = RELATIVE_CORNERS[corner_index]
                sx = self.origin_x + cx
                sy = self.origin_y + cy
                px = self.origin_x + self.player.x + PLAYER_SIZE // 2
                py = self.origin_y + self.player.y + PLAYER_SIZE // 2
                dx = (px - sx) / SHURIKEN_SPEED_FACTOR
                dy = (py - sy) / SHURIKEN_SPEED_FACTOR
                bounds = (
                    self.origin_x,
                    self.origin_y,
                    self.origin_x + ZONE_SIZE,
                    self.origin_y + ZONE_SIZE
                )
                self.balls.append(Ball(sx, sy, dx, dy, bounds))

            # Collision balle / joueur
            for b in self.balls:
                b.update()
                px = self.origin_x + self.player.x + PLAYER_SIZE // 2
                py = self.origin_y + self.player.y + PLAYER_SIZE // 2
                if abs(px - b.x) < (PLAYER_SIZE // 2 + BALL_WIDTH // 2) and \
                   abs(py - b.y) < (PLAYER_SIZE // 2 + BALL_HEIGHT // 2):
                    self.player.alive = False

            # Supprime les shurikens inactifs (hors zone)
            self.balls = [b for b in self.balls if b.active]

    def draw(self):
        if self.lost:
            # Affiche un écran noir avec "PERDU!" si le joueur est KO
            pyxel.rect(self.origin_x, self.origin_y, ZONE_SIZE, ZONE_SIZE, 0)
            pyxel.text(
                self.origin_x + ZONE_SIZE // 2 - 15,
                self.origin_y + ZONE_SIZE // 2,
                "PERDU!", 7
            )
        else:
            self.player.draw(self.origin_x, self.origin_y)
            for b in self.balls:
                b.draw()

# --- CLASSE PRINCIPALE ---
class Game:
    def __init__(self):
        pyxel.init(SCREEN_SIZE, SCREEN_SIZE, title="4 ninjas")
        pyxel.load("ninjas.pyxres")  # Chargement du fichier de sprites
        self.games = [MiniGame(i) for i in range(4)]
        self.restart_countdown = None  # None = pas de compte à rebours en cours
        self.restart_frames = 0        # Pour compter les frames du compte à rebours
        pyxel.run(self.update, self.draw)

    def update(self):
        # Redémarre tous les mini-jeux si on appuie sur R
        if pyxel.btnp(pyxel.KEY_R):
            self.games = [MiniGame(i) for i in range(4)]
            self.restart_countdown = None

        # Détecte la défaite globale et lance le compte à rebours si besoin
        if all(g.lost for g in self.games):
            if self.restart_countdown is None:
                self.restart_countdown = 3
                self.restart_frames = 0
            else:
                self.restart_frames += 1
                if self.restart_frames % 40 == 0:  # Une seconde (à 60 FPS)
                    self.restart_countdown -= 1
                    if self.restart_countdown == 0:
                        self.games = [MiniGame(i) for i in range(4)]
                        self.restart_countdown = None
        else:
            self.restart_countdown = None

        for g in self.games:
            g.update()

    def draw(self):
        pyxel.cls(5)  # Fond violet foncé
        for g in self.games:
            g.draw()

        # Lignes séparatrices au centre
        pyxel.line(ZONE_SIZE, 0, ZONE_SIZE, SCREEN_SIZE, 1)
        pyxel.line(0, ZONE_SIZE, SCREEN_SIZE, ZONE_SIZE, 1)

        # Numérotation des zones
        pyxel.text(ZONE_SIZE - 10, ZONE_SIZE - 10, "1", 13)
        pyxel.text(ZONE_SIZE + 5, ZONE_SIZE - 10, "2", 13)
        pyxel.text(ZONE_SIZE - 10, ZONE_SIZE + 5, "3", 13)
        pyxel.text(ZONE_SIZE + 5, ZONE_SIZE + 5, "4", 13)

        # Compte à rebours de redémarrage
        if self.restart_countdown is not None:
            s = f"Redémarrage dans {self.restart_countdown}"
            w = len(s) * 4
            pyxel.rect(SCREEN_SIZE // 2 - w // 2 - 4, SCREEN_SIZE // 2 - 10, w + 8, 20, 0)
            pyxel.text(SCREEN_SIZE // 2 - w // 2, SCREEN_SIZE // 2, s, 7)

# --- DÉMARRAGE DU JEU ---
Game()