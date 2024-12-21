# For the Players

## Preface

This is the accompanying README file for Ethan Mislang and Louise Vilar's implementation of the game "Battle City". It makes use of the Pyxel, a retro game engine for python. 

The specifications can be found in this Notion page https://dcs-jfmcoronel.notion.site/CS-12-23-2-MP-1-Battle-City-d1943f0e39f64c678de4188c7a676936#497739a636b14c59a403d0e8df1a59db .

A video demonstration of the final game is in this Google Drive folder: https://drive.google.com/drive/folders/1OGGjnLBiuvdtYAI87eXH27piuByuIPmH?usp=drive_link

Note: the highest phase that we have attained is **PHASE 3** (Completed all requirements)

## Controls

### Player Tank

- W:   Move up one cell
- A:    Move left one cell
- S:    Move down one cell
- D:   Move right one cell

- SPACEBAR: Shoot bullets
- SPACEBAR (Hold): Shoot bullets for fastest allowed rate of fire
- SPACEBAR (REPEAT): Shoot bullets in succession for fastest allowed rate of fire

### Game

- CTRL / Control    : Reset game
- Esc / Escape       : Stops the program (analogous to quit game) 
- Enter / Return     : Starts the game (if on the title screen), respawns the player (if already in game)

### Cheat code

This implementation contains a cheat code. Typing the string "OSTEP" at any point will give the player one (1) life.

## Gameplay

The objective of the game is to kill all **Enemy Tanks** within the alloted time of 2-minute per **Stages**. There are designated spawn points for enemies in the map, and the spawners cannot be killed. There is also a **Home Cell**, wherein if it is destroyed, the game is immediately over for the player regardless of **Token** and **Lives** left. 

# Code Explanation

## Environment 
Environment helps for the current display and transition of the game. Includes the following:
```
# Environment Variables

SCENE_TITLE = 0
SCENE_PLAY = 1
SCENE_GAMEOVER = 2
SCENE_VICTORY = 3
```

### Pyxelgrid

Most entities in the game go through Pyxelgrid, aside from the **PlayerBullets**, **EnemyBullets**, **EnemyLandmine** and other assets.

### Customization

They map layout of each stage is specified in their own respective text file. The acronyms are as follows:

1. "--" - Empty Cell
2. "PL" - Player
3. "HO" - Home cell
4. "PO" - Powerup
5. "SP" - Enemy Spawn
6. "E1" - Enemy 1
7. "E2" - Enemy 2
8. "ST" - Stone
9. "WA" - Water Block
10. "FO" - Forest Block
11. "BR" - Regular Brick
12. "CR" - Cracked Brick
13. "NE" - Northeast Leaning Mirror
14. "SE" - Southeast Leaning Mirror
15. "GR" - Grass
16. "LG" - Left grass
17. "TR" - Trees
18. "DO" - Door

### Caveats
There are a few requirements for the game to run properly. There must be at least one enemy in the map at initialization, there can only be one spawner, and there can only be one player tank.

## Player Tank
As the player, you control a blue-colored tank. 

- ### Bullets
   Pressing **[SPACEBAR]** allows the **Player Tank** to shoot **PlayerBullets**. Such **PlayerBullets** travels around 4 C/s (Cell per second)

- ### Lives
   The player tank has give (1) **Lives** for each insertion of **Token** at the start of the game. 

- ### Tokens
   By default, player is given (2) **Token** that can be used to respawn whenever **PlayerTank** dies from **EnemyBullets** or **EnemyLandmine**

## Enemy Tanks

Each **Stage** has respective number of enemy presence in the map. The following are the (2) Two types of Enemy Tanks.

- ### Regular Enemy Tank
    **RegularEnemyTank** are the counterpart of the **PlayerTank**. They are simple AI-controlled that moves and shoots **EnemyBullet** randomly at a given frame.  **PlayerTank** are neither allowed to pass through the **EnemyTanks** nor be damaged when adjacent to them.

- ### Landmine Tank
    Similar to **RegularEnemyTank**, **LandmineTank** are hostile **EnemyTank** but rather than firing **EnemyBullets**, these tanks plant **EnemyLandmine** on their position

## Stages

- ### Stage 1: Normal Map
   - Features all required cells in phase 3
   - Added other assets like doors, grass, and trees
- ### Stage 2: Maze Map 
   - Features all required cells in phase 3
   - Added other assets like doors, grass, and trees
- ### Stage 3: CS 12 Map 
   - Features all required cells in phase 3
   - Added other assets like doors, grass, and trees

## Sound Design
   The following are the sounds designed by *Ethan Mislang* using Pyxel Editor

- ### Bullet Firing 
- ### Bullet Explosion
- ### Enemy Tank Destruction
- ### Gameover and Gameend
- ### Stage Transition

## Sprites and Visual Designs
   The sprites and assets are designed by *Louise Vilar* using Pyxel Editor. 
```
resources.pyxres
```

## GameState
```
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
```
GameState, being a dataclass allows us to stack several in-game settings to control the current state of the game.

## Miscellaneous Features

- ### Timer

   Upon inserting a **Token** into the game, **Timer** of 2-minutes immediately starts. There are 2-minute alloted time for each **Stage**. When the **PlayerTank** is either **Dead** or the player pressed **Pause** the **Timer** stops and blinks to signal the player with the current time. When player pressed Enter/Return **Timer** will immediately **Resume** with the time it left off.

- **Timer** in **HUD** turns red when the time reaches the 30-second mark.

   If the timer runs out for each **Stage** the game immediately ends with **GameOver** even if the player still have **Lives** or **Token** left.

- ### Heads-Up Display (HUD)

   In **SCENE_PLAY**, players are guided and updated with sidebar that contains the basic **HUD** for **Lives**, **Timer**, **EnemyCount**, and **Token**. 


# CONTRIBUTIONS 

With each member unwavering effort and hardwork, Battle(C)ity is made possible. Herewith are the following contributions of members:

**MISLANG, Ethan Renell Sebastian**
- Pyxel Resources (Sound Design)
- Staging Mechanics (Including transitions)
- In-game Logic
- EnemyTank and LandmineTank
- Video Presentation
- Readme.md Formatting
...

**VILAR, Louise Gabiel R.**
- Pyxel Resources (Sprites, Text, Map Design)
- Environment and PyxelGrid Integration
- PlayerTank
- Miscellenaous Features (Timer)
- Gamestate Setting
- Readme.md Formatting
...
