import pygame
from player import Player
from TowerDefence import *
from player import Player
from load_game_parameters import load_game


# -------------------Pygame-------------------------
pygame.init()


GAME_SIZE = [160, 90]
WINDOW_SIZE = [GAME_SIZE[0]*5, GAME_SIZE[1]*5]
main_dis = pygame.display.set_mode(WINDOW_SIZE)

screen_manager = ScreenManager(WINDOW_SIZE, 5, main_dis)

clock = pygame.time.Clock()


# -------------- Load Textures ---------------

# ---utility---
screen_manager.load_pixel_texture("resources/Ghost.png", "ghost", True)
screen_manager.load_pixel_texture("resources/Arrows.png", "arrows", True)
screen_manager.load_pixel_texture("resources/Select.png", "select", True)
screen_manager.load_pixel_texture("resources/Currency.png", "currency", True)

screen_manager.load_pixel_texture("resources/Background.png", "background", True)

screen_manager.load_micro_font("resources/Micro_Chat.ttf")

# -----------------Game-------------------------
# main_player, tiles_manager, placeable, enemies
parameters = load_game("resources/stats.txt", screen_manager)

mainPlayer = parameters[0]
towerDef = TowerDefence(int(GAME_SIZE[0]/10), int(GAME_SIZE[1]/10)-1, parameters[1], parameters[2], parameters[3])

towerDef.calculate_pathfinding()

mainPlayer.position = [towerDef.base_pos[0]*10, towerDef.base_pos[1]*10]
# ---------------game loop-----------------------

space_hold = False
while True:
    dt = clock.tick(60) / 1000
    mouse_up_event = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:

            pygame.quit()
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_up_event = event.button

    # ------ Player Input --------
    keys = pygame.key.get_pressed()
    mouse_position = pygame.mouse.get_pos()

    if keys[pygame.K_SPACE] and not space_hold:
        towerDef.wave_manager.time_between_waves_timer = 0
        space_hold = True
    elif not keys[pygame.K_SPACE]:
        space_hold = False

    mainPlayer.userinput(keys, mouse_up_event, dt, towerDef)
    mainPlayer.calculate_selected(screen_manager.screen_to_pixel(mouse_position), towerDef.map)
    # ------ Physics --------
    towerDef.update(dt)
    mainPlayer.collision_with_tile(towerDef.map)
    mainPlayer.collision_with_tile(towerDef.map)
    # ------ Rendering -------

    screen_manager.fill((32, 18, 8))

    towerDef.draw(screen_manager)
    mainPlayer.draw(screen_manager)

    pygame.display.update()
