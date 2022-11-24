import os
import sys

import pygame
from Player import Player
from TowerDefence import *
from load_game_parameters import load_game
from SoundManager import SoundManager

# -------------------Pygame-------------------------
pygame.init()


GAME_SIZE = [160, 90]
WINDOW_SIZE = [GAME_SIZE[0]*5*2, GAME_SIZE[1]*5*2]
main_dis = pygame.display.set_mode(WINDOW_SIZE)

screen_manager = ScreenManager(WINDOW_SIZE, 10, main_dis)
sound_manager = SoundManager()

clock = pygame.time.Clock()


# -------------- Load Textures ---------------

# ---utility---
screen_manager.load_pixel_texture("resources/textures/Line.png", "line", True)
screen_manager.load_pixel_texture("resources/textures/Bar.png", "bar", True)

screen_manager.load_pixel_texture("resources/textures/Music.png", "music_icon", True)
screen_manager.load_pixel_texture("resources/textures/Sounds.png", "sound_icon", True)

screen_manager.load_pixel_texture("resources/textures/Ghost.png", "ghost", True)
screen_manager.load_pixel_texture("resources/textures/Arrows.png", "arrows", True)
screen_manager.load_pixel_texture("resources/textures/Select.png", "select", True)
screen_manager.load_pixel_texture("resources/textures/Currency.png", "currency", True)
screen_manager.load_pixel_texture("resources/textures/Background.png", "background", True)

screen_manager.load_micro_font("resources/fonts/Micro_Chat.ttf")

# --- default sounds
sound_manager.load_sound("break_block", "resources/sounds/break_block.wav")
sound_manager.load_sound("place_block", "resources/sounds/place_block.wav")
sound_manager.load_sound("place_turret", "resources/sounds/place_turret.wav")
sound_manager.load_sound("damage_base", "resources/sounds/damage_base.wav")

# --- Load Music ---
music_directory = "resources/music"
for i in os.listdir(music_directory):
    sound_manager.load_music(f"{music_directory}/{i}")


# -----------------Game-------------------------
# main_player, tiles_manager, placeable, enemies
parameters = load_game("resources/stats.txt", screen_manager, sound_manager)

mainPlayer = parameters[0]
towerDef = TowerDefence(int(GAME_SIZE[0]/10), int(GAME_SIZE[1]/10)-1, parameters[1], parameters[2], parameters[3], sound_manager)

towerDef.calculate_pathfinding()

mainPlayer.position = [towerDef.base_pos[0]*10, towerDef.base_pos[1]*10]
sound_manager.set_music_volume(.01)
sound_manager.play_random_track()
# ---------------game loop-----------------------


def darken_screen(amount):
    screen_manager.fill_with_opacity((0, 0, 0), amount)


def pause_screen():
    darken_screen(150)
    sound_manager.pause_music()


def unpause_screen():
    sound_manager.unpause_music()


def draw_soundbars(sm: ScreenManager):
    sm.pixel_rect((13, 7, 3), 10, 13, 32, 4)
    sm.pixel_blit(0, 10, "music_icon")
    sm.pixel_blit(10, 10, "line")
    sm.pixel_blit(20, 10, "line")
    sm.pixel_blit(30, 10, "line")

    sm.pixel_rect((13, 7, 3), 10, 33, 32, 4)
    sm.pixel_blit(0, 30, "sound_icon")
    sm.pixel_blit(10, 30, "line")
    sm.pixel_blit(20, 30, "line")
    sm.pixel_blit(30, 30, "line")

    sm.pixel_blit(10 + sound_manager.music_volume * 30, 10, "bar")
    sm.pixel_blit(10 + sound_manager.sound_volume * 30, 30, "bar")


paused = False
game_over = False
while True:
    dt = clock.tick(60) / 1000
    mouse_up_event = -1
    keys = pygame.key.get_pressed()
    mouse_position = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

        if event.type == SoundManager.NEXT_SONG:
            # sound_manager.play_next_track()
            sound_manager.play_random_track()

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_up_event = event.button

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE and not game_over:
                paused = not paused
                if paused:
                    pause_screen()
                    pos = screen_manager.window_size[0]/2 - int(len("Paused")/2)*4 * screen_manager.pixel_size
                    screen_manager.normal_micro_font(pos, 5, "Paused", (240, 240, 240))
                else:
                    unpause_screen()

            if event.key == pygame.K_RETURN and game_over:
                towerDef.reset()
                mainPlayer.position = [towerDef.base_pos[0] * 10, towerDef.base_pos[1] * 10]
                game_over = False

            if event.key == pygame.K_SPACE and len(towerDef.wave_manager.wave_spawn_monster_list) == 0 and len(towerDef.enemies) == 0:
                towerDef.wave_manager.time_between_waves_timer = 0
    if paused:
        draw_soundbars(screen_manager)
        if pygame.mouse.get_pressed()[0]:
            if 5 * screen_manager.pixel_size < mouse_position[0] < 45 * screen_manager.pixel_size:
                volume = min(max((mouse_position[0] / screen_manager.pixel_size - 10) / 30, 0), 1)
                if abs(mouse_position[1]-150) < 20:  # top bar

                    sound_manager.set_music_volume(volume)

                if abs(mouse_position[1]-350) < 20:  # top bar

                    sound_manager.set_sound_volume(volume)

    if not paused and not game_over:
        # ------ Player Input --------

        mainPlayer.userinput(keys, mouse_up_event, dt, towerDef)
        mainPlayer.calculate_selected(screen_manager.screen_to_pixel(mouse_position), towerDef.map)
        # ------ Physics --------
        if towerDef.update(dt):
            game_over = True

        mainPlayer.collision_with_tile(towerDef.map)
        mainPlayer.collision_with_tile(towerDef.map)
        # ------ Rendering -------

        screen_manager.fill((32, 18, 8))

        towerDef.draw(screen_manager)
        mainPlayer.draw(screen_manager)

        if game_over:
            pause_screen()
            text = "Game Over!"
            pos = screen_manager.window_size[0] / 2 - int(len(text) / 2) * 5 * screen_manager.pixel_size
            screen_manager.normal_micro_font(pos, 3 * screen_manager.pixel_size, text, (255, 0, 0))

            # play again
            text = "Return to play again!"
            pos = screen_manager.window_size[0] / 2 - int(len(text) / 2) * 5 * screen_manager.pixel_size
            screen_manager.normal_micro_font(pos, 13 * screen_manager.pixel_size, text, (240, 240, 240))

            # wave text
            text = f"You made it to wave {towerDef.wave_manager.wave_number}!"
            pos = screen_manager.window_size[0] / 2 - int(len(text) / 2) * 5 * screen_manager.pixel_size
            screen_manager.normal_micro_font(pos, 33 * screen_manager.pixel_size, text, (255, 80, 54))

            # money text
            text = f"You total worth was {towerDef.total_player_currency}!"
            pos = screen_manager.window_size[0] / 2 - int(len(text) / 2) * 5 * screen_manager.pixel_size
            screen_manager.normal_micro_font(pos, 43 * screen_manager.pixel_size, text, (95, 183, 243))

    pygame.display.update()

