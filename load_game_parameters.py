from SoundManager import SoundManager
from Player import Player
from ScreenManager import ScreenManager
from TowerDefence import TileManager, PlaceableTile
from Turret import Turret
from Enemy import Enemy


def parse_int(text):
    return int(text.split(" = ")[-1].strip())


def parse_float(text):
    return float(text.split(" = ")[-1].strip())


def parse_string(text):
    return text.split(" = ")[-1].strip().replace("\"", "")


def parse_color(text):
    values = text.split(" = ")[-1].strip().replace("(", "").replace(")", "")
    # 10, 10, 10
    parsed = values.split(",")
    return_list = []
    for p in parsed:
        return_list.append(int(p.strip()))
    return return_list


def parse_player(lines, i, sm: ScreenManager):
    texture_name = parse_string(lines[i+1])
    speed = parse_float(lines[i+2])
    damage = parse_float(lines[i+3])
    sm.load_pixel_texture(texture_name, texture_name, True)
    return Player(texture_name, speed, damage)


def parse_tile(lines, i, sm: ScreenManager, tm: TileManager):
    name = parse_string(lines[i+1])
    texture_name = parse_string(lines[i+2])
    difficulty = parse_float(lines[i+3])
    collision = bool(parse_int(lines[i+4]))
    sm.load_pixel_texture(texture_name, texture_name, True)
    tm.add_tile(name, texture_name, difficulty, collision)


def parse_placeable_tile(lines, i, sm: ScreenManager, tm:TileManager):
    texture_name = parse_string(lines[i+1])
    cost = parse_int(lines[i+2])
    tile_name = parse_string(lines[i+3])
    sm.load_pixel_texture(texture_name, texture_name, True)
    return PlaceableTile(texture_name, cost, tm.get_tile(tile_name))


def parse_placeable_turret(lines, i, sm: ScreenManager, sound_m: SoundManager):
    texture_name = parse_string(lines[i+1])
    cost = parse_int(lines[i+2])
    t_range = parse_float(lines[i+3])
    damage = parse_float(lines[i+4])
    fire_rate = parse_float(lines[i+5])
    hardness = parse_float(lines[i+6])
    turret_texture_name = parse_string(lines[i+7])
    laser_thickness = parse_int(lines[i+8])
    laser_color = parse_color(lines[i+9])
    laser_show_time = parse_float(lines[i+10])
    laser_sound = parse_string(lines[i + 11])

    sm.load_pixel_texture(texture_name, texture_name, True)
    sm.load_pixel_texture(turret_texture_name, turret_texture_name, True)
    sound_m.load_sound(laser_sound, laser_sound)
    turret = Turret(-1, [0, 0], t_range, damage, fire_rate, hardness, None, turret_texture_name, laser_sound)
    turret.set_drawing_vars(laser_thickness, laser_color, laser_show_time)
    return PlaceableTile(texture_name, cost, turret)


def parse_enemy(lines, i, sm: ScreenManager):
    texture_name = parse_string(lines[i+1])
    cost = parse_int(lines[i+2])
    health = parse_int(lines[i+3])
    speed = parse_float(lines[i+4])
    damage = parse_float(lines[i+5])
    value = parse_float(lines[i+6])
    sm.load_pixel_texture(texture_name, texture_name, True)
    # cost, health, speed, damage, value, texture_name
    return [cost, health, speed, damage, value, texture_name]


def load_game(stat, sm: ScreenManager, sound_m: SoundManager):
    main_player = None
    tiles_manager = TileManager()
    placeable = []
    enemies = []

    with open(stat, "r") as f:
        lines = f.readlines()
        index = 0
        while index < len(lines):
            if "[PLAYER]" in lines[index]:
                main_player = parse_player(lines, index, sm)
            if "[TILE]" in lines[index]:
                parse_tile(lines, index, sm, tiles_manager)
            if "[PLACEABLE_TILE]" in lines[index]:
                placeable.append(parse_placeable_tile(lines, index, sm, tiles_manager))
            if "[PLACEABLE_TURRET]" in lines[index]:
                placeable.append(parse_placeable_turret(lines, index, sm, sound_m))
            if "[ENEMY]" in lines[index]:
                enemies.append(parse_enemy(lines, index, sm))

            index += 1
    return main_player, tiles_manager, placeable, enemies
