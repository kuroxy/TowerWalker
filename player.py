import pygame
import math
from ScreenManager import ScreenManager
from TowerDefence import MapManager


class Player:
    def __init__(self):
        self.texture_name = "player"
        self.position: list[float, float] = [0, 0]
        self.SPEED: float = 50
        self.damage = 1

        self.facing_direction: int = 0  # n e s w
        self.selected_tile_position: list[int, int] = None
        self.selected_tile = None
        self.tile_size = 10

    def calculate_selected(self, mouse_pos, mm: MapManager):
        difference_x = mouse_pos[0]-self.position[0]
        difference_y = mouse_pos[1]-self.position[1]
        if abs(difference_x) > abs(difference_y):  # x is dominant
            self.facing_direction = 1 if difference_x > 0 else 3

        else:  # y is dominant
            self.facing_direction = 2 if difference_y > 0 else 0

        #               --- Selected tile (position) ---
        tile_position_x = round((self.position[0]) / self.tile_size)
        tile_position_y = round((self.position[1]) / self.tile_size)

        old_selected_position = self.selected_tile_position.copy() if self.selected_tile_position else None

        if self.facing_direction == 0:
            self.selected_tile_position = [tile_position_x, tile_position_y - 1]
        elif self.facing_direction == 1:
            self.selected_tile_position = [tile_position_x + 1, tile_position_y]
        elif self.facing_direction == 2:
            self.selected_tile_position = [tile_position_x, tile_position_y + 1]
        elif self.facing_direction == 3:
            self.selected_tile_position = [tile_position_x - 1, tile_position_y]

        if old_selected_position != self.selected_tile_position:
            self.selected_tile = mm.get_tile(self.selected_tile_position[0], self.selected_tile_position[1])

    def userinput(self, keys, mouse_event, dt, td):
        # --- movement ---
        direction = [0, 0]
        if keys[pygame.K_w]:
            direction[1] -= 1
        if keys[pygame.K_s]:
            direction[1] += 1
        if keys[pygame.K_a]:
            direction[0] -= 1
        if keys[pygame.K_d]:
            direction[0] += 1

        self.move(direction, dt, td.map)

        # --- breaking tiles ---
        if mouse_event == 1 and self.selected_tile is not None:
            td.map.damage_tile(self.selected_tile_position[0],self.selected_tile_position[1], self.damage)
        if mouse_event == 3:
            td.place_placeable(self.selected_tile_position[0], self.selected_tile_position[1])
        if mouse_event == 4:
            td.change_placeable(1)
        if mouse_event == 5:
            td.change_placeable(-1)

    def move(self, direction: list, dt, mm: MapManager):
        length = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        if length != 0:
            direction[0] /= length
            direction[1] /= length
            x_change = direction[0] * dt * self.SPEED
            y_change = direction[1] * dt * self.SPEED
            self.position[0] += x_change
            self.position[1] += y_change

    def draw(self, sm: ScreenManager):
        sm.part_pixel_blit(self.position[0], self.position[1], self.texture_name)
        sm.part_pixel_blit(self.selected_tile_position[0] * 10, self.selected_tile_position[1] * 10, "select")

    def collision_with_tile(self, mm: MapManager):
        small_x = math.floor((self.position[0]) / self.tile_size)
        big_x = math.ceil((self.position[0]) / self.tile_size)

        small_y = math.floor((self.position[1]) / self.tile_size)
        big_y = math.ceil((self.position[1]) / self.tile_size)
        # A0 A1
        # B0 B1

        positions = [(big_x, big_y), (big_x, small_y), (small_x, big_y), (small_x, small_y)]

        for position in positions:
            tile = mm.get_tile(position[0], position[1])
            if tile is not None and tile.collision:
                self.collision_response(position[0]*self.tile_size, position[1]*self.tile_size)
                return

    def collision_response(self, x, y):
        vector_x = self.position[0] - x
        vector_y = self.position[1] - y

        if vector_y * vector_y > vector_x * vector_x:  # y response
            if vector_y > 0:
                self.position[1] = y + self.tile_size
            else:
                self.position[1] = y - self.tile_size

        else:
            if vector_x > 0:
                self.position[0] = x + self.tile_size
            else:
                self.position[0] = x - self.tile_size
