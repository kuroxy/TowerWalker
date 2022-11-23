import random

from Enemy import Enemy
from ScreenManager import ScreenManager
from SoundManager import SoundManager
from Turret import Turret
from WaveManager import WaveManager


class Tile:
    def __init__(self, texture_name: str, diff: float, collidable: bool, turret_id: int = None) -> None:

        self.difficulty = diff
        self.collision = collidable
        self.texture_name = texture_name

        self.connected_turret_id = turret_id

    def draw(self, sm: ScreenManager, x: int, y: int):
        """ draws a tile on a surface
        :param sm: screenManager to draw on
        :param x: x coordinate to draw
        :param y: y coordinate to draw
        """
        sm.pixel_blit(x, y, self.texture_name)


class TileManager:
    def __init__(self):
        self.tiles = {}

    def add_tile(self, name: str, texture_name: str, difficulty: float, collidable: bool):
        """ adds a tile to the tile manager
        :param name: the name of the tile
        :param texture_name: the name of the texture
        :param difficulty: how difficult it is to move through that tile
        :param collidable: if it is walkable or false if you need to mine it
        """
        self.tiles[name.lower()] = Tile(texture_name, difficulty, collidable)

    def get_tile(self, name: str) -> Tile:
        """ gets the tile from name
        :param name: the name of the tile
        :return: the tile requested
        """
        if name.lower() not in self.tiles:
            raise Exception("Not a valid tile in TileManager")

        return self.tiles[name.lower()]


def create_tileManager() -> TileManager:
    """ creates a tile manager
    set the current tiles and loads the textures
    :return: tile manager
    """
    tm = TileManager()
    tm.add_tile("Empty", "empty", 1, False)
    tm.add_tile("Base", "base", 1, False)
    tm.add_tile("Spawner", "spawner", 1, False)

    tm.add_tile("StoneWall", "stonewall", 5, True)

    return tm


class MapManager:
    def __init__(self, map_size_x: int, map_size_y: int, tm: TileManager):
        self.map_size = [map_size_x, map_size_y]
        self.tm: TileManager = tm

        # --- setting the map ---
        self.map: list[list[Tile]] = None
        self.fill_map("stonewall")

        # --- setting the damage map ---
        self.damage_map: list[list[float]] = [[0 for _ in range(self.map_size[0])] for _ in range(self.map_size[1])]

        # --- pathfinding  ---
        self.default_path: list[list[any]] = [[-1 for _ in range(self.map_size[0])] for _ in range(self.map_size[1])]

    def fill_map(self, tile_name: str):
        """ fills the whole map with 1 type of tile
        :param tile_name: name of the tile
        """
        self.map = [[self.tm.get_tile(tile_name) for _ in range(self.map_size[0])] for _ in range(self.map_size[1])]
        self.damage_map = [[self.tm.get_tile(tile_name).difficulty for _ in range(self.map_size[0])] for _ in range(self.map_size[1])]

    def set_tile(self, x: int, y: int, tile: Tile):
        """ set a tile from given coordinate
        :param x: x coordinate
        :param y: y coordinate
        :param tile: tile to set
        """
        if x < 0 or x >= self.map_size[0] or y < 0 or y >= self.map_size[1]:
            raise Exception("out of bounds of the map")

        self.map[y][x] = tile
        self.damage_map[y][x] = tile.difficulty

    def get_tile(self, x: int, y: int) -> Tile:
        """ gives the tile from given coordinate
        :param x: x coord
        :param y: y coord
        :return: the tile from requested coordinates
        """
        if x < 0 or x >= self.map_size[0] or y < 0 or y >= self.map_size[1]:
            return None

        return self.map[y][x]

    def draw_map(self, sm: ScreenManager):
        """ Draw the map to the surface
        :param sm: ScreenManager to draw
        """
        for y in range(self.map_size[1]):
            for x in range(self.map_size[0]):
                self.map[y][x].draw(sm, x*10, y*10)

    def draw_debug_path_map(self, sm: ScreenManager):
        for y in range(self.map_size[1]):
            for x in range(self.map_size[0]):
                sm.pixel_text_blit(x*10, y*10, str(self.default_path[y][x]), 10, (255, 255, 255))

    # --- damage map ---

    def damage_tile(self, x: int, y: int, damage: float) -> None:
        """ damages a block at given coordinate
        :param x: x coord
        :param y: y coord
        :param damage: how much damage is dealt
        """
        self.damage_map[y][x] -= damage

    def update_damage_map(self, sound_m):
        """ updates the damage map removes tiles that are completely damaged
        """
        for y in range(self.map_size[1]):
            for x in range(self.map_size[0]):
                if self.damage_map[y][x] <= 0:
                    if self.map[y][x] != self.tm.get_tile("empty") and self.map[y][x] != self.tm.get_tile("base") and self.map[y][x] != self.tm.get_tile("spawner"):
                        sound_m.play_sound("break_block")
                        self.map[y][x] = self.tm.get_tile("empty")
                        self.damage_map[y][x] = self.tm.get_tile("empty").difficulty

    # --- pathfinding ---

    def generate_default_path(self, goal_x, goal_y):
        """ calculate the route from every position to base
        """
        self.default_path = [[-1 for _ in range(self.map_size[0])] for _ in range(self.map_size[1])]
        self.default_path[goal_y][goal_x] = 0
        self.updateRouteTile(goal_x, goal_y)

    def updateRouteTile(self, x: int, y: int):
        """ updates one tile in default path
        :param x: x coordinate
        :param y: y coordinate
        """
        current_value = self.default_path[y][x]
        positions: list[list[int, int]] = []
        if x > 0:
            positions.append([x-1, y])
        if x < self.map_size[0]-1:
            positions.append([x + 1, y])
        if y > 0:
            positions.append([x, y-1])
        if y < self.map_size[1]-1:
            positions.append([x, y+1])

        for position in positions:
            value = self.default_path[position[1]][position[0]]
            new_difficulty = self.map[position[1]][position[0]].difficulty

            new_value = current_value + new_difficulty
            if new_value < value or value == -1:  # if it is shorter make this the new one. or if it is -1 (not set)

                self.default_path[position[1]][position[0]] = new_value
                self.updateRouteTile(position[0], position[1])


class PlaceableTile:
    def __init__(self, texture_name: str, cost: int, tile):
        self.texture_name = texture_name
        self.cost = cost
        self.type = tile


class TowerDefence:
    def __init__(self, x_size: int, y_size: int, tm: TileManager, placeables: list[PlaceableTile], wave_enemies, sound_m: SoundManager) -> None:
        self.tm: TileManager = tm
        self.sound_m: SoundManager = sound_m

        # tiles map with type of tiles
        self.map: MapManager = MapManager(x_size, y_size, self.tm)
        self.map.fill_map("stonewall")

        # enemy buildings positions
        self.spawner_pos: list[int, int] = [0, 0]  # position of the spawner
        self.base_pos: list[int, int] = [0, 0]  # position of the spawner

        self.base_health = 100

        self.generate_utilities()  # setting random positions for the spawner and the base

        # objects
        self.wave_manager: WaveManager = WaveManager(self, wave_enemies)
        self.enemies: list[Enemy] = []
        self.turret_custom_id: int = 0
        self.turrets: list[Turret] = []

        # --- player attributes ---
        self.player_currency: int = 0
        self.total_player_currency = self.player_currency

        self.placeable_tile_list_index = 0
        self.placeable_tile_list = []
        # --- placeable tiles ---
        for placeable in placeables:
            if isinstance(placeable.type, Tile):
                self.placeable_tile_list.append(placeable)
            elif isinstance(placeable.type, Turret):
                placeable.type.td = self
                self.placeable_tile_list.append(placeable)

        self.reset()

    def reset(self):
        self.player_currency = 25
        self.total_player_currency = self.player_currency
        self.wave_manager.reset()
        self.map.fill_map("stonewall")
        self.base_health = 100
        self.generate_utilities()
        self.enemies = []

    def generate_utilities(self) -> None:
        """ creating and setting the spawner_pos and base_pos to a random position
        """
        # generating spawner position
        self.spawner_pos = [0, random.randint(0, self.map.map_size[1] - 1)]  # always on the left of the map
        self.map.set_tile(self.spawner_pos[0], self.spawner_pos[1], self.tm.get_tile("spawner"))

        # generating base position
        self.base_pos = [self.map.map_size[0] - 1, random.randint(0, self.map.map_size[1] - 1)]  # always on the right
        self.map.set_tile(self.base_pos[0], self.base_pos[1], self.tm.get_tile("base"))

    def calculate_pathfinding(self):
        self.map.generate_default_path(self.base_pos[0], self.base_pos[1])

    def add_enemy(self, en):
        self.enemies.append(en)

    def place_turret(self, x, y, custom_turret):
        tr = custom_turret.copy()
        tr.position = [x*10, y*10]
        tr.turret_id = self.turret_custom_id

        self.turrets.append(tr)
        self.map.set_tile(x, y, Tile(custom_turret.texture_name, tr.hardness, True, self.turret_custom_id))
        self.turret_custom_id += 1

    def place_placeable(self, x, y):
        if x < 0 or x >= self.map.map_size[0] or y < 0 or y >= self.map.map_size[1]:
            # out of bounds
            print("out of bounds")
            return

        if self.map.get_tile(x, y).texture_name != self.tm.get_tile("empty").texture_name:
            # not an empty place
            print("non empty")
            return

        selected = self.placeable_tile_list[self.placeable_tile_list_index]

        if selected.cost > self.player_currency:
            # not enough money
            return

        if isinstance(selected.type, Tile):
            self.sound_m.play_sound("place_block")
            self.map.set_tile(x, y, selected.type)
        elif isinstance(selected.type, Turret):
            self.sound_m.play_sound("place_turret")
            self.place_turret(x, y, selected.type)
        self.player_currency -= int(selected.cost)

    def change_placeable(self, amount):
        self.placeable_tile_list_index += amount
        self.placeable_tile_list_index %= len(self.placeable_tile_list)

    def update(self, dt: float):
        # wave management
        self.wave_manager.update(dt)

        # turrets damage check
        for turret in self.turrets:
            tile_position = turret.position
            tile_position = [int(tile_position[0]/10), int(tile_position[1]/10)]
            if self.map.get_tile(tile_position[0], tile_position[1]).connected_turret_id != turret.turret_id:
                print(self.map.get_tile(tile_position[0], tile_position[1]).connected_turret_id)
                print(turret.turret_id)

                self.turrets.remove(turret)

        # update turrets
        for turret in self.turrets:
            turret.update(dt, self.sound_m)

        # update enemies
        for enemy in self.enemies:
            enemy.update(dt)

            if enemy.health <= 0:
                self.player_currency += int(enemy.value)
                self.total_player_currency += int(enemy.value)
                self.enemies.remove(enemy)

        # damage base
        for enemy in self.enemies:
            if enemy.old_objective == self.base_pos:
                self.base_health -= enemy.damage
                self.enemies.remove(enemy)
                self.sound_m.play_sound("damage_base")

        # update map
        self.map.update_damage_map(self.sound_m)
        self.calculate_pathfinding()

        if self.base_health <= 0:
            return True

    def draw(self, sm: ScreenManager, debug: bool = False):
        # drawing the map
        self.map.draw_map(sm)

        if debug:
            self.map.draw_debug_path_map(sm)

        # drawing enemies
        for enemy in self.enemies:
            enemy.draw(sm)

        for turret in self.turrets:
            turret.draw(sm)
        sm.pixel_render()

        # player interface background
        for x in range(self.map.map_size[0]):
            sm.pixel_blit(x*10, self.map.map_size[1]*10, "background")

        # placeable tiles interface
        sm.pixel_blit(0, self.map.map_size[1] * 10, "arrows")  # money

        selected = self.placeable_tile_list[self.placeable_tile_list_index]
        sm.pixel_blit(1 * 10, self.map.map_size[1] * 10, selected.texture_name)
        color = (255, 255, 255) if selected.cost <= self.player_currency else (165, 24, 24)
        sm.pixel_micro_font(2 * 10, self.map.map_size[1] * 10 + 1, str(selected.cost).zfill(2), color)

        # wave indicator
        sm.pixel_blit(4 * 10, self.map.map_size[1] * 10, "ghost")  # skull/ghost

        sm.pixel_micro_font(5 * 10, self.map.map_size[1] * 10 + 1, str(self.wave_manager.wave_number), (243, 226, 177))

        if len(self.enemies) == 0 and self.wave_manager.time_between_waves_timer != 10:
            timeleft = int(self.wave_manager.time_between_waves_timer)
            color = (255, 0, 0) if timeleft % 2 == 0 else (127, 0, 0)
            sm.pixel_micro_font(7 * 10, self.map.map_size[1] * 10 + 1, f"({timeleft})", color)

        # base health
        sm.pixel_blit(9 * 10, self.map.map_size[1] * 10-1, self.tm.get_tile("base").texture_name)
        color = (165, 24, 24)
        if self.base_health > 90:
            color = (53, 178, 58)
        elif self.base_health > 75:
            color = (77, 212, 100)
        elif self.base_health > 50:
            color = (247, 196, 57)
        elif self.base_health > 25:
            color = (255, 80, 54)

        sm.pixel_micro_font(10*10, self.map.map_size[1] * 10 + 1, str(int(self.base_health)), color)
        # diamond image + player currency amount
        sm.pixel_blit((self.map.map_size[0]-4)*10, self.map.map_size[1]*10, "currency")  # money
        sm.pixel_micro_font((self.map.map_size[0]-3)*10+1, self.map.map_size[1]*10+1, str(self.player_currency), (95, 183, 243))

