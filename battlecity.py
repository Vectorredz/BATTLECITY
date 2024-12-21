'''
This is the acronyms for the map:

-- - Empty Cell

PL - Player
HO - Home cell

PO - Powerup

SP - Enemy Spawn
E1 - Enemy 1
E2 - Enemy 2

ST - Stone
WA - Water Block
FO - Forest Block
GR - Grass
LG - Left grass
TR -  Trees
MS - Mini stones
DO - door
BR - Regular Brick
CR - Cracked Brick

NE - Northeast Leaning Mirror
SE - Southeast Leaning Mirror

This is the designation for the sounds from resources.pyxres:

Sound 0 - Player hit
Sound 1 - Powerup get
Sound 2 - Bullet fired
Sound 3 - Bullet destroyed
Sound 4 - Enemy tank destroyed


'''

import pyxel
import pyxelgrid as pg
from random import randint
from dataclasses import dataclass
import time

SCENE_TITLE = 0
SCENE_PLAY = 1
SCENE_GAMEOVER = 2
SCENE_VICTORY = 3

ROWS = 22
COLS = 35
DIMS = 10

SCREEN_WIDTH = COLS * DIMS
SCREEN_HEIGHT = ROWS * DIMS

TAB_WIDTH = 50
TAB_HEIGHT = SCREEN_HEIGHT
TAB_X = SCREEN_WIDTH - TAB_WIDTH
TAB_Y = 0

COLLISION_COLS = COLS - (TAB_WIDTH // 10)-1

HUD_WIDTH = 100
HUD_HEIGHT = 20
HUD_X = SCREEN_WIDTH - HUD_WIDTH
HUD_Y = 0

NORTH = 10
SOUTH = 20
EAST = 30
WEST = 40

DIRECTIONS = [NORTH, SOUTH, EAST, WEST]

random_text=randint(1,1000)

initial_map=[]

walls = {}
mirrors = {}
stones = []
waters = []
forests = []
powerups = []
Homecell = []
grass = []
trees = []
left_grass = []
door = []

TANK_RNG=(1, 200)

bullets = []
BULLET_SPEED = 6
FIRE_RATE = 10 

enemy_bullets = []
enemies = []

def check_enemy_collision(player_pos, enemy_pos):
    if player_pos == enemy_pos:
        return True
    return False
    
def is_walkable_cell(x: int, y: int):
    if (x,y) in walls:
        return False
    if (x,y) in stones:
        return False
    if (x,y) in mirrors:
        return False
    if (x,y) in enemies_landmine_positions+enemies_tank_positions:
        return False
    if (x,y) in waters:
        return False
    if (x,y) in Homecell:
        return False
    return True

@dataclass
class GameState:
    player_lives: int
    game_token: int
    player_is_alive: bool
    is_game_over: bool
    is_victory: bool
    is_reset_game: bool
    is_pause_game: bool
    is_death_pause: bool
    is_game_end: bool
    stage: int
    stage_time: int
    scene: int

class Background:
    def __init__(self):
        self.stars = []
        for _ in range(100):
            self.stars.append(
                (
                    pyxel.rndi(0, SCREEN_WIDTH),
                    pyxel.rndi(0, SCREEN_WIDTH),
                    pyxel.rndf(1, 2.5),
                )
            )

    def update(self):
        for i, (x, y, speed) in enumerate(self.stars):
            y += speed
            if y >= pyxel.height:
                y -= pyxel.height
            self.stars[i] = (x, y, speed)

    def draw(self):
        for x, y, speed in self.stars:
            pyxel.pset(x, y, 100 if speed > 1.8 else 200)

class PlayerBullet:
    def __init__(self, x: int, y: int, direction: int, game_state):
        self.x = x
        self.y = y
        self.direction = direction
        self.game_state = game_state
        self.is_active = True
        bullets.append(self)

    def update(self):
        cell_y = (self.y+DIMS//2) // DIMS
        cell_x = (self.x+DIMS//2) // DIMS

        if (cell_y, cell_x) in waters:
            if self.direction == NORTH:
                self.y -= 1
            elif self.direction == SOUTH:
                self.y += 1
            elif self.direction == WEST:  
                self.x -= 1
            elif self.direction == EAST:
                self.x += 1
        else:
            if self.direction == NORTH:
                self.y -= BULLET_SPEED
            elif self.direction == SOUTH:
                self.y += BULLET_SPEED
            elif self.direction == WEST:
                self.x -= BULLET_SPEED
            elif self.direction == EAST:
                self.x += BULLET_SPEED
        
        cell_y = (self.y+DIMS//2) // DIMS
        cell_x = (self.x+DIMS//2) // DIMS
     
        if cell_y < 0 or cell_x < 0 or cell_x >= COLS or cell_y >= ROWS:
            pyxel.play(2, 3)
            bullets.remove(self)
            return

        if (cell_y, cell_x) in Homecell:
            pyxel.play(2, 3)
            bullets.remove(self)
            self.game_state.is_game_end = True
            self.game_state.player_is_alive = False

        if (cell_y, cell_x) in mirrors:
            mirror_type = mirrors[(cell_y, cell_x)]

            if mirror_type == '/':
                if self.direction == NORTH:
                    self.direction = EAST
                elif self.direction == SOUTH:
                    self.direction = WEST
                elif self.direction == EAST:
                    self.direction = NORTH
                elif self.direction == WEST:
                    self.direction = SOUTH
            elif mirror_type == '\\':
                if self.direction == EAST:
                    self.direction = SOUTH
                elif self.direction == WEST:
                    self.direction = NORTH
                elif self.direction == SOUTH:
                    self.direction = EAST
                elif self.direction == NORTH:
                    self.direction = WEST
                return 

        if (cell_y, cell_x) in walls:
            wall_type, hitpoints = walls[(cell_y, cell_x)]
            if hitpoints > 1:
                walls[(cell_y, cell_x)] = ('cracked', hitpoints - 1)
            else:
                del walls[(cell_y, cell_x)]
            pyxel.play(2, 3)            
            bullets.remove(self)

        elif (cell_y, cell_x) in stones:
            pyxel.play(2, 3)
            bullets.remove(self)

        for enemy_bullet in enemy_bullets:
            enemy_x = enemy_bullet.x // DIMS
            enemy_y = enemy_bullet.y // DIMS
            if (cell_y, cell_x) == (enemy_y, enemy_x):
                pyxel.play(2, 3)
                enemy_bullets.remove(enemy_bullet)
                bullets.remove(self)
                self.is_active = True

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 40, 0, 8, 8, 0)

class EnemyBullet:
    def __init__(self, x: int, y: int, direction: int, game_state):
        self.x = x
        self.y = y
        self.game_state=game_state
        self.direction=direction
        enemy_bullets.append(self)

    def update(self):
        cell_y = (self.y+DIMS//2) // DIMS
        cell_x = (self.x+DIMS//2) // DIMS

        if (cell_y, cell_x) in Homecell:
            enemy_bullets.remove(self)
            self.game_state.is_game_end = True
            self.game_state.player_is_alive = False


        if (cell_y, cell_x) in waters:
            if self.direction == NORTH:  # NORTH
                self.y -= 1
            elif self.direction == SOUTH:  # SOUTH
                self.y += 1
            elif self.direction == WEST:  # WEST  
                self.x -= 1
            elif self.direction == EAST:  # EAST
                self.x += 1
        else:
            if self.direction == NORTH:
                self.y -= BULLET_SPEED
            elif self.direction == SOUTH:
                self.y += BULLET_SPEED
            elif self.direction == WEST:
                self.x -= BULLET_SPEED
            elif self.direction == EAST:
                self.x += BULLET_SPEED
        
        cell_y = (self.y+DIMS//2) // DIMS
        cell_x = (self.x+DIMS//2) // DIMS
     
        if cell_y < 0 or cell_x < 0 or cell_x >= COLS or cell_y >= ROWS:
            pyxel.play(2, 3)
            enemy_bullets.remove(self)
            return

        if (cell_y, cell_x) in mirrors:
            mirror_type = mirrors[(cell_y, cell_x)]

            if mirror_type == '/':
                if self.direction == NORTH:
                    self.direction = EAST
                elif self.direction == SOUTH:
                    self.direction = WEST
                elif self.direction == EAST:
                    self.direction = NORTH
                elif self.direction == WEST:
                    self.direction = SOUTH
            elif mirror_type == '\\':
                if self.direction == EAST:
                    self.direction = SOUTH
                elif self.direction == WEST:
                    self.direction = NORTH
                elif self.direction == SOUTH:
                    self.direction = EAST
                elif self.direction == NORTH:
                    self.direction = WEST
                return 

        if (cell_y, cell_x) in walls:
            pyxel.play(2, 3)
            wall_type, hitpoints = walls[(cell_y, cell_x)]
            if hitpoints > 1:
                walls[(cell_y, cell_x)] = ('cracked', hitpoints - 1)
            else:
                del walls[(cell_y, cell_x)]
            enemy_bullets.remove(self)

        elif (cell_y, cell_x) in stones:
            pyxel.play(2, 3)
            enemy_bullets.remove(self)

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 40, 8, 8, 8, 0)

class EnemyLandmine:
    def __init__(self, x: int, y: int, game_state):
        self.x = x
        self.y = y
        self.game_state=game_state
        enemy_bullets.append(self)

    def update(self):
        cell_y = (self.y+DIMS//2) // DIMS
        cell_x = (self.x+DIMS//2) // DIMS

        if (cell_y, cell_x) in Homecell:
            pyxel.play(2, 3)
            enemy_bullets.remove(self)
            self.game_state.is_game_end = True
            self.game_state.player_is_alive = False


    def draw(self):
        pyxel.blt(self.x, self.y, 0, 42, 17, 5, 5,0)

class PlayerTank:
    def __init__(self, battle_city):
        self.battle_city = battle_city
        self.game_state = self.battle_city.game_state
        self.bounds = self.battle_city.r - 1, self.battle_city.c - 1
        self.tank_position: tuple[int, int]
        self.initial_tank_position: tuple[int, int]
        self.direction = NORTH
        self.powerup_state = False
        self.powerup_start_time: int
        self.consecutive_enemy_kills = 0

    def respawn(self):
        self.tank_position = self.initial_tank_position
        self.direction = NORTH
        self.powerup_state = False
        self.game_state.player_is_alive = True
        self.consecutive_enemy_kills = 0

    def update(self):
        if not self.game_state.is_game_end:
            if self.game_state.player_lives > 0:
                for enemy_bullet in enemy_bullets:
                    enemy_cell_y = ((enemy_bullet.y + DIMS//2)// DIMS)   
                    enemy_cell_x = ((enemy_bullet.x + DIMS//2)// DIMS)
                    if self.tank_position == (enemy_cell_y, enemy_cell_x):
                        pyxel.play(0,0)
                        self.game_state.player_lives -= 1
                        if self.game_state.player_lives <=0:
                            self.game_state.player_is_alive = False
                            self.game_state.is_game_over = True
                        if enemy_bullet in enemy_bullets:
                            enemy_bullets.remove(enemy_bullet)
                for bullet in bullets:
                    cell_y = (bullet.y + DIMS//2) // DIMS
                    cell_x = (bullet.x + DIMS//2) // DIMS
                    if self.tank_position == (cell_y, cell_x):
                        pyxel.play(0,0)
                        self.game_state.player_lives -= 1
                        self.game_state.player_is_alive = False
                        self.game_state.is_game_over = True
                        if bullet in bullets:
                            bullets.remove(bullet)

        if self.consecutive_enemy_kills==5:
            self.consecutive_enemy_kills=0
            random_x = randint(0, ROWS)
            random_y = randint(0, COLLISION_COLS)

            while (random_x, random_y) in entities:
                random_x = randint(0, ROWS)
                random_y = randint(0, COLLISION_COLS)

            if is_walkable_cell(random_x, random_y):
               powerups.append((random_x,random_y))

        if self.tank_position in powerups:
            pyxel.play(0, 1)
            self.powerup_state = True
            self.start_time=int(time.time())
            powerups.remove(self.tank_position)

        i, j = self.tank_position
        new_positon = self.tank_position

        holdf = 12
        repeatf = 6

        if self.game_state.player_is_alive:
            if pyxel.btnp(pyxel.KEY_W, hold=holdf, repeat=repeatf) and i > 0 and is_walkable_cell(i-1, j):  # North # enemytank
                self.direction = NORTH
                new_positon = (i-1, j)
            elif pyxel.btnp(pyxel.KEY_S, hold=holdf, repeat=repeatf) and i < self.battle_city.r - 1 and is_walkable_cell(i+1, j):  # South
                self.direction = SOUTH
                new_positon = (i+1, j)
            elif pyxel.btnp(pyxel.KEY_D, hold=holdf, repeat=repeatf) and j < self.battle_city.c - 1 and is_walkable_cell(i, j+1):  # East
                self.direction = EAST
                new_positon = (i, j+1)
            elif pyxel.btnp(pyxel.KEY_A, hold=holdf, repeat=repeatf) and j > 0 and is_walkable_cell(i, j-1):  # West
                self.direction = WEST
                new_positon = (i, j-1)

        if not any(check_enemy_collision(new_positon, enemy) for enemy in enemies):
            self.tank_position = new_positon

        if self.game_state.player_is_alive:
            if pyxel.btnp(pyxel.KEY_SPACE):
                if self.powerup_state:
                    current_time=int(time.time())
                    if current_time-self.start_time<=5:
                        can_fire=True
                    else:
                        self.powerup_state=False
                        can_fire=False
                else:
                    can_fire = True
                    for bullet in bullets:
                        if bullet.is_active:
                            can_fire = False
                        break
                    
                if can_fire:
                    tank_x = self.tank_position[1] * self.battle_city.dim
                    tank_y = self.tank_position[0] * self.battle_city.dim
                    bullet_x, bullet_y = tank_x, tank_y
                    if self.direction == NORTH:
                        bullet_y -= DIMS//2
                    elif self.direction == SOUTH:
                        bullet_y += DIMS//2
                    elif self.direction == EAST:
                        bullet_x += DIMS//2
                    elif self.direction == WEST:
                        bullet_x -= DIMS//2

                    PlayerBullet(bullet_x, bullet_y, self.direction, self.game_state)
                    pyxel.play(0, 2)

    def draw(self):
        x = self.tank_position[1] * self.battle_city.dim
        y = self.tank_position[0] * self.battle_city.dim
        if self.direction == NORTH:
            pyxel.blt(x, y, 0, 0, 0, 8, 8)
        elif self.direction == SOUTH:
            pyxel.blt(x, y, 0, 8, 0, 8, 8)
        elif self.direction == EAST:
            pyxel.blt(x, y, 0, 16, 0, 8, 8)
        elif self.direction == WEST:
            pyxel.blt(x, y, 0, 24, 0, 8, 8)

class EnemyTank:
    def __init__(self, battle_city, position):
        self.battle_city = battle_city
        self.game_state=self.battle_city.game_state
        self.player_tank = battle_city.player_tank
        self.player_bullet = battle_city.player_bullet
        self.bounds = self.battle_city.r - 1, self.battle_city.c - 1
        self.enemy_tank_position = position
        self.direction = DIRECTIONS[randint(0,3)]
        self.fire_cooldown = 0 

    def update(self):
        for bullet in bullets:
            cell_y = ((bullet.y + DIMS//2)// DIMS)
            cell_x = ((bullet.x + DIMS//2)// DIMS)
            if self.enemy_tank_position==(cell_y, cell_x):
                self.player_tank.consecutive_enemy_kills+=1
                pyxel.play(2, 4)
                enemies_tank.remove(self)
                enemies_tank_positions.remove(self.enemy_tank_position)
                if bullet in bullets:
                    bullets.remove(bullet)
            if (cell_y, cell_x) == ((self.player_bullet.y) // DIMS, (self.player_bullet.x) // DIMS):
                if bullet in bullets:  
                    bullets.remove(bullet)
            
        i, j = self.enemy_tank_position
        new_enemy_tank_position = self.enemy_tank_position
        random=randint(1,200)
        if random==2 and i > 0 and is_walkable_cell(i-1,j):  # North
            self.direction = NORTH
            new_enemy_tank_position = (i-1, j)
        elif random==3 and i < self.battle_city.r - 1 and is_walkable_cell(i+1,j):  # South
            self.direction = SOUTH
            new_enemy_tank_position = (i+1, j)
        elif random==4 and j < self.battle_city.c - 1 and is_walkable_cell(i,j+1):  # East
            self.direction = EAST
            new_enemy_tank_position = (i, j+1)
        elif random==5 and j > 0 and is_walkable_cell(i,j-1):  # West
            self.direction = WEST
            new_enemy_tank_position = (i, j-1)
        
        if not any(check_enemy_collision(new_enemy_tank_position, enemy.enemy_tank_position) for enemy in enemies) and new_enemy_tank_position != self.player_tank.tank_position:
            self.enemy_tank_position = new_enemy_tank_position

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        if 6<=random<=10:
            enemy_tank_x = self.enemy_tank_position[1] * DIMS
            enemy_tank_y = self.enemy_tank_position[0] * DIMS
            enemy_bullet_x, enemy_bullet_y = enemy_tank_x, enemy_tank_y
            if self.direction == NORTH:  # NORTH
                enemy_bullet_y -= DIMS//2
            elif self.direction == SOUTH:  # SOUTH
                enemy_bullet_y += DIMS//2
            elif self.direction == EAST:  # EAST
                enemy_bullet_x += DIMS//2
            elif self.direction == WEST:  # WEST
                enemy_bullet_x -= DIMS//2 
            pyxel.play(1, 2)
            EnemyBullet(enemy_bullet_x, enemy_bullet_y, self.direction, self.game_state)
            self.fire_cooldown = FIRE_RATE
           
    def draw(self):
        pass

class LandmineTank:
    def __init__(self, battle_city, position):
        self.battle_city = battle_city
        self.player_tank = battle_city.player_tank
        self.player_bullet = battle_city.player_bullet
        self.bounds = self.battle_city.r - 1, self.battle_city.c - 1
        self.enemy_tank_position = position
        self.direction = DIRECTIONS[randint(0,3)]
        self.fire_cooldown = 0 

    def update(self):
        for bullet in bullets:
            cell_y = ((bullet.y + DIMS//2)// DIMS)
            cell_x = ((bullet.x + DIMS//2)// DIMS)
            if self.enemy_tank_position==(cell_y, cell_x):
                self.player_tank.consecutive_enemy_kills+=1
                pyxel.play(2, 4)
                enemies_landmine.remove(self)
                enemies_landmine_positions.remove(self.enemy_tank_position)
                if bullet in bullets:
                    bullets.remove(bullet)
            if (cell_y, cell_x) == ((self.player_bullet.y) // DIMS, (self.player_bullet.x) // DIMS):
                if bullet in bullets:  
                    bullets.remove(bullet)

        i, j = self.enemy_tank_position
        new_landmine_tank_position = self.enemy_tank_position

        random_bound_1, random_bound_2 = TANK_RNG
        result=randint(random_bound_1, random_bound_2)

        if result==2 and i > 0 and is_walkable_cell(i-1,j):  # North
            self.direction = NORTH
            new_landmine_tank_position = (i-1, j)
        elif result==3 and i < self.battle_city.r - 1 and is_walkable_cell(i+1,j):  # South
            self.direction = SOUTH
            new_landmine_tank_position = (i+1, j)
        elif result==4 and j < self.battle_city.c - 1 and is_walkable_cell(i,j+1):  # East
            self.direction = EAST
            new_landmine_tank_position = (i, j+1)
        elif result==5 and j > 0 and is_walkable_cell(i,j-1):  # West
            self.direction = WEST
            new_landmine_tank_position = (i, j-1)
        
        if not any(check_enemy_collision(new_landmine_tank_position, enemy.enemy_tank_position) for enemy in enemies) and new_landmine_tank_position != self.player_tank.tank_position:
            self.enemy_tank_position = new_landmine_tank_position

        if 6<=result<=10:
            enemy_tank_x = self.enemy_tank_position[1] * self.battle_city.dim
            enemy_tank_y = self.enemy_tank_position[0] * self.battle_city.dim
            if self.direction == NORTH:  # NORTH
                enemy_bullet_x =  enemy_tank_x 
                enemy_bullet_y =  enemy_tank_y 
            elif self.direction == SOUTH:  # SOUTH
                 enemy_bullet_x =  enemy_tank_x
                 enemy_bullet_y =  enemy_tank_y 
            elif self.direction == EAST:  # EAST
                 enemy_bullet_x =  enemy_tank_x
                 enemy_bullet_y =  enemy_tank_y
            elif self.direction == WEST:  # WEST
                 enemy_bullet_x =  enemy_tank_x 
                 enemy_bullet_y =  enemy_tank_y

            can_fire=True
            global enemy_bullets
            for enemy_bullet in enemy_bullets:
                if (enemy_bullet_x, enemy_bullet_y)==(enemy_bullet.x, enemy_bullet.y):
                    can_fire=False
                    break
            bullet_cell_y = ((enemy_bullet_y + DIMS//2)// DIMS)
            bullet_cell_x = ((enemy_bullet_x + DIMS//2)// DIMS)
      
            if can_fire and is_walkable_cell(bullet_cell_x, bullet_cell_y):
                pyxel.play(1, 2)
                EnemyLandmine(enemy_bullet_x, enemy_bullet_y, self.battle_city.game_state)

enemies_tank = []
enemies_tank_positions = [enemy.enemy_tank_position for enemy in enemies_tank]

enemies_landmine = []
enemies_landmine_positions = [enemy.enemy_tank_position for enemy in enemies_landmine]

enemies = enemies_tank+enemies_landmine

entities = [list(walls.keys())+list(mirrors.keys())+stones+waters+forests+powerups+Homecell+ enemies]

class BattleCity(pg.PyxelGrid[int]):
    def __init__(self):
        super().__init__(r=ROWS, c=COLLISION_COLS+1, dim=DIMS)
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="BATTLE(C)ITY")
        pyxel.load("resources.pyxres")
        self.game_state = GameState(player_lives=1, player_is_alive=True, game_token=2, is_game_over=False, is_death_pause=False,is_pause_game=False, is_victory=False, is_reset_game=False, is_game_end=False, stage=1, stage_time=120, scene=SCENE_TITLE)
        self.player_bullet = PlayerBullet(SCREEN_HEIGHT, SCREEN_WIDTH, NORTH, self.game_state)
        self.player_tank = PlayerTank(self)
        self.spawner_position: tuple[int, int]
        self.init_map()
        self.init_time()
        self.background = Background()
        pyxel.run(self.update, self.draw)
        
    def init(self) -> None:
        pyxel.cls(0)
        for i in range(self.r):
            for j in range(self.c):
                self[i, j] = 0

    def init_time(self):
        self.start_play_time = 0
        self.pause_start_time = 0
        self.total_pause_duration = 0
        self.countdown_time = self.game_state.stage_time
        self.remaining_time = self.countdown_time
        self.pause_time = False

    def cheat_codes(self):
        self.game_state.player_lives += 1
        return 
    
    def transition_between_stages(self):
        global initial_map, walls, mirrors, stones, enemies_landmine, enemies_tank, waters, forests, powerups, entities, Homecell, trees, grass, left_grass, bullets, enemy_bullets, door
        initial_map=[]
        walls={}
        mirrors={}
        stones=[]
        waters=[]
        enemies_tank=[]
        enemies_landmine=[]
        bullets=[]
        enemy_bullets=[]
        waters=[]
        powerups=[]
        forests=[]
        Homecell = []
        trees = []
        grass = []
        left_grass = []
        door = []
        pyxel.play(0, 7)
        if self.game_state.stage==1 and self.game_state.is_victory==True:
            self.game_state.stage+=1
            self.game_state.is_victory=False
            self.game_state.player_is_alive= True
            self.game_state.is_reset_game=False
            self.game_state.stage_time = 120
            self.game_state.scene = SCENE_PLAY
            self.player_tank.consecutive_enemy_kills = 0
            self.player_tank.powerup_state=False
            self.game_state.is_game_end = False
            self.init_map()
            self.init_time()
            self.start_play_time = time.time()
        if self.game_state.stage==2 and self.game_state.is_victory==True:
            self.game_state.stage+=1
            self.game_state.is_victory=False
            self.game_state.player_is_alive= True
            self.game_state.is_reset_game=False
            self.game_state.stage_time = 120
            self.game_state.scene = SCENE_PLAY
            self.player_tank.consecutive_enemy_kills = 0
            self.player_tank.powerup_state=False
            self.game_state.is_game_end = False
            self.init_map()
            self.init_time()
            self.start_play_time = time.time()

    def init_map(self):
        global initial_map, walls, mirrors, stones, enemies, waters, forests, powerups, trees, grass
        if self.game_state.stage == 1 and not self.game_state.is_reset_game:
            initial_map=[]
            file_path = 'stage1.txt'
            with open(file_path, 'r') as f:
                [initial_map.append(eval(line)) for line in f.readlines()]
        if self.game_state.stage==2 and not self.game_state.is_reset_game:
            initial_map=[]
            file_path = 'stage2.txt'
            with open(file_path, 'r') as f:
                [initial_map.append(eval(line)) for line in f.readlines()]
        if self.game_state.stage==3 and not self.game_state.is_reset_game:
            initial_map=[]
            file_path = 'stage3.txt'
            with open(file_path, 'r') as f:
                [initial_map.append(eval(line)) for line in f.readlines()]
        # else:
        #     raise ValueError('stage 1 at 2 lang meron :(')

        for row in range(len(initial_map)):
            for col in range(len(initial_map[0])):
                item=initial_map[row][col]
                if item == 'PL':
                    self.player_tank.tank_position=(row, col)
                    self.player_tank.initial_tank_position=(row, col)
                    self.player_tank.respawn()
                elif item == 'HO':
                    Homecell.append((row, col))
                elif item == 'SP':
                    self.spawner_position=(row, col)
                elif item == 'E1':
                    enemies_tank.append(EnemyTank(self, (row, col)))
                elif item == 'E2':
                    enemies_landmine.append(LandmineTank(self, (row, col)))
                elif item == 'ST':
                    stones.append((row, col))
                elif item == 'BR':
                    walls[(row, col)] = ('brick', 2)
                elif item == 'CR':
                    walls[(row, col)] = ('cracked', 1)
                elif item == 'NE':
                    mirrors[(row, col)]='/'
                elif item == 'SE':
                    mirrors[(row, col)] = '\\'
                elif item == 'WA':
                    waters.append((row, col))
                elif item == 'FO':
                    forests.append((row, col))
                elif item == 'PO':
                    powerups.append((row,col))
                elif item == 'GR':
                    grass.append((row,col))
                elif item == 'TR':
                    trees.append((row, col))
                elif item == 'LG':
                    left_grass.append((row,col))
                elif item == 'DO':
                    door.append((row, col))
                else:
                    continue
    
    def toggle_pause(self):
        if self.pause_time:
            self.pause_time = False
            self.total_pause_duration += time.time() - self.pause_start_time 
        else:
            self.pause_time = True
            self.pause_start_time = time.time()

    def update_time(self):
        if not self.pause_time:
            self.elapsed_time = time.time() - self.start_play_time - self.total_pause_duration
            self.remaining_time = self.countdown_time - self.elapsed_time
        if self.remaining_time <= 0:
            self.game_state.is_game_end = True
            self.remaining_time = 0

         
    def update(self):
        self.background.update()

        # initialize time
        if self.game_state.scene == SCENE_PLAY:
            self.update_time()

        if self.remaining_time <= 0:
            self.game_state.is_game_end = True
        # quit game
        if pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()
        
        # cheat code: 'OSTEP'
        if pyxel.btn(pyxel.KEY_O) and pyxel.btn(pyxel.KEY_S) and pyxel.btn(pyxel.KEY_T) and pyxel.btn(pyxel.KEY_E) and pyxel.btn(pyxel.KEY_P):
            if self.game_state.scene==SCENE_PLAY and self.game_state.player_lives>0:
                self.cheat_codes()
        
        # pause game
        if pyxel.btnp(pyxel.KEY_TAB):
            # must not happen simultaenously (pausing and dying)
            if not self.game_state.is_pause_game and not self.game_state.is_death_pause:
                self.game_state.is_pause_game = True
                self.toggle_pause() 

        # resume game
        if pyxel.btnp(pyxel.KEY_RETURN):
            if self.pause_time and self.game_state.is_pause_game:
                self.game_state.is_pause_game = False
                self.toggle_pause()
            if pyxel.btnp(pyxel.KEY_RETURN):
                if self.game_state.scene == SCENE_TITLE:
                    self.game_state.scene = SCENE_PLAY
                    self.start_play_time = time.time()
        elif self.game_state.scene == SCENE_PLAY:
            self.update_entities()
            if self.game_state.game_token < 0: 
                self.game_state.scene = SCENE_GAMEOVER
            if self.game_state.is_death_pause:
                self.game_state.is_death_pause = False
                self.toggle_pause()
            elif self.game_state.stage==1 and self.game_state.is_victory == True:
                self.transition_between_stages()
            elif self.game_state.stage==2 and self.game_state.is_victory == True:
                self.transition_between_stages()
            elif self.game_state.stage==3 and self.game_state.is_victory == True:
                self.game_state.scene = SCENE_VICTORY

        # restart game
        if pyxel.btn(pyxel.KEY_CTRL):
            global enemies_tank, enemies_landmine, bullets, enemy_bullets, walls, mirrors, stones, waters, forests, powerups, Homecell, left_grass, grass, trees
            enemies_landmine=[]
            enemies_tank=[]
            bullets=[]
            enemy_bullets=[]
            walls = {}
            mirrors = {}
            stones = []
            waters = []
            forests = []
            powerups = []
            Homecell = []
            left_grass = []
            grass = []
            trees = []
            self.game_state.player_lives = 1
            self.game_state.player_is_alive=True
            self.game_state.game_token=2
            self.game_state.is_game_over=False
            self.game_state.is_death_pause=False
            self.pause_time=False
            self.game_state.is_pause_game=False
            self.game_state.is_victory=False
            self.game_state.is_reset_game=False 
            self.game_state.is_game_end=False
            self.game_state.stage=1 
            self.game_state.stage_time=120
            self.game_state.scene=SCENE_TITLE
            self.init_map()
            self.init_time()

        global enemies_tank_positions, enemies_landmine_positions, enemies, entities
        enemies_landmine_positions=[enemy.enemy_tank_position for enemy in enemies_landmine]
        enemies_tank_positions=[enemy.enemy_tank_position for enemy in enemies_tank]
        enemies=enemies_landmine+enemies_tank

        entities = [list(walls.keys())+list(mirrors.keys())+stones+waters+forests+powerups+Homecell+enemies_tank_positions+enemies_landmine_positions]

        if is_walkable_cell(self.spawner_position[0], self.spawner_position[1]):
            i, j = self.spawner_position
            random=randint(1,100)
            if random==4:
                type=randint(0,1)
                if type==0:
                    enemies_tank.append(EnemyTank(self, self.spawner_position))
                else:
                    enemies_landmine.append(LandmineTank(self, self.spawner_position))

    def update_entities(self):
        if not self.game_state.is_pause_game and not self.game_state.is_game_end:
            if not enemies:
                self.game_state.is_victory = True
            self.player_tank.update()
            for bullet in bullets:
                bullet.update()
            for enemy_bullet in enemy_bullets:
                enemy_bullet.update()
            for enemy in enemies:
                enemy.update()

    def draw(self) -> None:
        pyxel.cls(0)
        self.background.draw()
        if self.game_state.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.game_state.scene == SCENE_PLAY:
            self.draw_play_scene()
            if self.game_state.is_pause_game == True:
                self.draw_pause_screen()
            elif self.game_state.is_game_end == True:
                self.toggle_pause()
                self.draw_game_end()
            elif self.game_state.is_death_pause == True:
                self.toggle_pause()
        elif self.game_state.scene == SCENE_GAMEOVER:
            self.draw_gameover_scene()
        elif self.game_state.scene == SCENE_VICTORY:
            self.draw_victory_scene()

    def draw_game_end(self):
        pyxel.play(2, 3)
        pyxel.blt(100,70,1,0,160,16,16,0)
        pyxel.blt(100+15,70,1,16,160,16,16,0)
        pyxel.blt(100+30,70,1,32,160,16,16,0)
        pyxel.blt(100+45,70,1,48,160,16,16,0)
        pyxel.blt(100+60,70,1,64,160,16,16,0)
        pyxel.blt(100+75,70,1,80,160,16,16,0)
        pyxel.blt(100+90,70,1,96,160,16,16,0)
        pyxel.blt(100+105,70,1,112,160,16,16,0)
        if not self.remaining_time <= 0:
            pyxel.text(((SCREEN_HEIGHT)//2)-20, 130, "- NO TOKEN LEFT OR HOME DESTROYED - ", 10)
            pyxel.text((SCREEN_HEIGHT)//2, 140, "< PRESS CTRL TO RESTART >", 7)
        else:
            pyxel.text((SCREEN_HEIGHT)//2, 140, "< PRESS CTRL TO RESTART >", 7)


    def draw_pause_screen(self):
        pyxel.text((SCREEN_HEIGHT+50)//2, 100, "- GAME PAUSED - ", 7)
        pyxel.text((SCREEN_HEIGHT+15)//2, 120, "< PRESS ENTER TO RESUME >", 7)

    def draw_title_scene(self):
        if random_text==2:
            text='juanchover'
        elif 3<=random_text<=199:
            text='louise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\nlouise_gabriel:\n'
        elif 200<=random_text<=400:
            text='getaway driver'
        elif 401<=random_text<=600:
            text='N world!!'
        elif 601<=random_text<=800:
            text='thats crazy ah'
        else:
            text='Mansure'

        pyxel.text((SCREEN_WIDTH)//2-30, (SCREEN_HEIGHT//2)+30, text, pyxel.frame_count % 16)
        pyxel.text(((SCREEN_WIDTH)//2)-60, 110, "- PRESS ENTER TO INSERT TOKEN -", randint(2,9))
        # B
        pyxel.blt(100,70,1,0,96,16,16,0)
        # A
        pyxel.blt(100+15,70,1,16,96,16,16,0)
        # T
        pyxel.blt(100+30,70,1,32,96,16,16,0)
        # T
        pyxel.blt(100+45,70,1,48,96,16,16,0)
        # L
        pyxel.blt(100+60,70,1,64,96,16,16,0)
        # E
        pyxel.blt(100+75,70,1,80,96,16,16,0) 
        pyxel.blt(100+90,70,1,96,96,16,16,0)
        pyxel.blt(100+105,70,1,112,96,16,16,0)
        pyxel.blt(100+120,70,1,128,96,16,16,0)
        pyxel.blt(100+135,70,1,144,96,16,16,0)
    
    def draw_play_scene(self):
        self.draw_grid()
        self.draw_tab()
        self.draw_hud()

    def draw_gameover_scene(self):
        if self.game_state.game_token >= 1:
            pyxel.play(2, 3)
            pyxel.text((SCREEN_HEIGHT)//2, 120, "- PRESS ENTER TO RESPAWN -", 7)
            pyxel.text((SCREEN_HEIGHT+80)//2, 130, f"Token: {self.game_state.game_token}", 10)
            pyxel.blt(100,70,1,0,160,16,16,0)
            pyxel.blt(100+15,70,1,16,160,16,16,0)
            pyxel.blt(100+30,70,1,32,160,16,16,0)
            pyxel.blt(100+45,70,1,48,160,16,16,0)
            pyxel.blt(100+60,70,1,64,160,16,16,0)
            pyxel.blt(100+75,70,1,80,160,16,16,0)
            pyxel.blt(100+90,70,1,96,160,16,16,0)
            pyxel.blt(100+105,70,1,112,160,16,16,0)
            if pyxel.btnp(pyxel.KEY_RETURN):
                pyxel.play(2, 3)
                self.game_state.game_token -=1; self.game_state.player_lives = 1; self.game_state.player_is_alive = True
                self.player_tank.respawn()
                global bullets, enemy_bullets
                bullets=[]
                enemy_bullets=[]
                self.game_state.scene = SCENE_PLAY
    
        elif self.game_state.game_token <= 0 or self.game_state.player_lives <= 0 and self.game_state.is_game_over:
            pyxel.play(2, 3)
            pyxel.blt(100,70,1,0,160,16,16,0)
            pyxel.blt(100+15,70,1,16,160,16,16,0)
            pyxel.blt(100+30,70,1,32,160,16,16,0)
            pyxel.blt(100+45,70,1,48,160,16,16,0)
            pyxel.blt(100+60,70,1,64,160,16,16,0)
            pyxel.blt(100+75,70,1,80,160,16,16,0)
            pyxel.blt(100+90,70,1,96,160,16,16,0)
            pyxel.blt(100+105,70,1,112,160,16,16,0)
            self.game_state.is_game_end = True
        
    def draw_victory_scene(self):
        if self.game_state.is_victory:
            pyxel.blt(100+30,70,1,0,144,16,16,0)
            pyxel.blt(100+45,70,1,16,144,16,16,0)
            pyxel.blt(100+60,70,1,32,144,16,16,0)
            pyxel.blt(100+75,70,1,48,144,16,16,0)
            pyxel.blt(100+90,70,1,64,144,16,16,0)
            pyxel.blt(100+105,70,1,80,144,16,16,0)
            pyxel.blt(100+120,70,1,96,144,16,16,0)
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                pyxel.quit()

    def draw_tab(self):
        pyxel.rect(TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT, 3)
        pyxel.rect(TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT//3, 0) 
        pyxel.rectb(TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT//3, 7) 
        pyxel.rectb(TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT//8, 7)
        pyxel.rectb(TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT, 7)  

    def draw_hud(self):
        self.secs = int(self.remaining_time) % 60
        self.mins = int((self.remaining_time // 60)) 
        pyxel.text(HUD_X + 63, HUD_Y + 5, f"STAGE {self.game_state.stage}",  12)
        if self.pause_time or self.game_state.is_death_pause:
            pyxel.text(HUD_X + 72, HUD_Y+ 16, f"{self.mins:02}:{self.secs:02}",  pyxel.frame_count % 16)
        elif self.remaining_time <= 30:
            pyxel.text(HUD_X + 72, HUD_Y+ 16, f"{self.mins:02}:{self.secs:02}",  8)
        else:
            pyxel.text(HUD_X + 72, HUD_Y+ 16, f"{self.mins:02}:{self.secs:02}",  7)
        pyxel.blt(HUD_X + 60, HUD_Y + 14.5, 1,32,64,8,8,0)
        pyxel.text(HUD_X + 63, HUD_Y+ 33, f"LIVES: {self.game_state.player_lives}",  8)
        pyxel.blt(HUD_X + 53, HUD_Y + 32, 1,0,64,8,8,0)
        pyxel.text(HUD_X + 65, HUD_Y + 45, f"TOKEN: {self.game_state.game_token}",  10)
        pyxel.blt(HUD_X + 53, HUD_Y + 44, 1,16,64,8,8)
        pyxel.text(HUD_X + 65, HUD_Y + 58, f"ENEMY: {len(enemies)}",  9)
        pyxel.blt(HUD_X + 53, HUD_Y + 57, 1,24,64,8,8,0)

    def draw_grid(self):
        for i in range(self.r):
            for j in range(self.c):
                x = j * self.dim
                y = i * self.dim
                self.draw_cell(i, j, x, y)
                self.pre_draw_grid(i, j, x, y)

    def draw_cell(self, i: int, j: int, x: int, y: int) -> None:
        if self.game_state.player_lives < 1:
            self.game_state.is_death_pause = True
            self.toggle_pause()
            self.draw_gameover_scene()
    
            
        if (i, j) in enemies_tank_positions:
            pyxel.blt(x, y, 1, enemies_tank[enemies_tank_positions.index((i, j))].direction, 10, 10, 10)
        elif (i, j) in enemies_landmine_positions:
            pyxel.blt(x, y, 1, enemies_landmine[enemies_landmine_positions.index((i, j))].direction, 20, 10, 10)
        elif (i, j) == self.player_tank.tank_position:
                if self.game_state.player_lives > 0:
                    pyxel.blt(x, y, 1, self.player_tank.direction, 0, 18, 18)
                else:
                    pyxel.rect(x, y, self.dim, self.dim, 0)
        elif (i,j) in trees:
            pyxel.blt(x,y,1,30,42,10,10,1)
        elif (i,j) in grass:
            pyxel.blt(x,y,1,40,42,10,10,1)
        
        elif (i,j) in left_grass:
            pyxel.blt(x,y,1,50,42,10,10,1)
        elif (i, j) in powerups:
            pyxel.blt(x, y, 1, 20, 52, 16, 16, 0)
        elif (i, j) in Homecell:
            pyxel.blt(x, y, 1, 20, 42, 10, 10)
        elif (i, j) == self.spawner_position:
            pyxel.blt(x, y, 1, 0, 52, 10, 10)        
        elif (i, j) in walls:
            wall_type, hitpoints = walls[(i,j)]
            if wall_type == 'brick' and hitpoints > 1:
                pyxel.blt(x, y, 1, 0, 32,10,10)
            elif wall_type == 'cracked' and hitpoints == 1:
                pyxel.blt(x, y, 1, 10, 32,10,10)
            else:
                pyxel.rect(x, y, self.dim, self.dim, 0)  
        elif (i,j) in stones:
            pyxel.blt(x,y,1,30,32,10,10)
        elif  (i,j) in mirrors:
            mirror_type = mirrors[(i,j)]
            if mirror_type == '/':
                pyxel.blt(x,y,1,10,42,10,10)
            elif mirror_type == '\\':
                pyxel.blt(x,y,1,0,42,10,10)
        elif (i, j) in waters:
            pyxel.blt(x, y, 1, 20, 32, 10, 10)
        else:
            pyxel.rect(x, y, self.dim, self.dim, 0)
        
        for bullet in bullets:
            bullet.draw()
        
        for enemy_bullet in enemy_bullets:
            enemy_bullet.draw()

    def pre_draw_grid(self, i, j, x , y) -> None:
        if (i,j) in forests:
            pyxel.blt(x, y, 1, 40, 32, 10, 10,0)
        elif (i,j) in door:
            pyxel.blt(x,y,1,60,32,10,10,0)

    def post_draw_grid(self) -> None:
        pass

game = BattleCity()

game.run(title="BATTLE(C)ITY", fps=30)
