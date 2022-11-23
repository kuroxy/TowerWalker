import math
import random

from ScreenManager import ScreenManager


class Enemy:
    def __init__(self, mm, spawn_x: int, spawn_y: int, texture_name):
        self.map = mm
        self.texture_name = texture_name

        # --- Enemy stats ---
        self.position: list[float, float] = [0, 0]

        self.health: float = 100
        self.speed: float = 1
        self.damage: float = 5

        self.value = 1
        # --- movement ----
        self.progress: float = 0

        self.old_objective: list[int, int] = None
        self.new_objective: list[int, int] = [spawn_x, spawn_y]
        # --- spawning enemy calculations ---
        self.set_new_objective()

    def set_enemy_stats(self, texture_name, health, speed, damage, value):
        self.texture_name = texture_name
        self.health = health
        self.speed = speed
        self.damage = damage
        self.value = value

    def set_new_objective(self):
        positions: list[list[int, int]] = []
        curr_x = self.new_objective[0]
        curr_y = self.new_objective[1]

        positions.append([curr_x, curr_y])

        if curr_x > 0:
            positions.append([curr_x - 1, curr_y])
        if curr_x < self.map.map_size[0] - 1:
            positions.append([curr_x + 1, curr_y])
        if curr_y > 0:
            positions.append([curr_x, curr_y - 1])
        if curr_y < self.map.map_size[1] - 1:
            positions.append([curr_x, curr_y + 1])

        best_pos = [0, 0]
        smallest = math.inf
        for position in positions:
            value = self.map.default_path[position[1]][position[0]]
            if value < smallest or (value == smallest and random.random() > .5):
                smallest = value
                best_pos = position

        self.old_objective = self.new_objective
        self.new_objective = best_pos

    def update(self, dt: float):
        """ updates the enemy by moving or dealing damage to a tile
        :param dt: delta time
        """
        if not self.map.get_tile(self.new_objective[0], self.new_objective[1]).collision:
            # movable
            self.progress += dt*self.speed
        else:
            self.map.damage_tile(self.new_objective[0], self.new_objective[1], dt*self.damage)

        if self.progress >= 1:  # reached the end of its new tile
            self.progress = 0  # reset progress
            self.set_new_objective()  # sets the new objective

        self.calculate_position()

    def calculate_position(self):
        """ calculates the drawing position
        """
        x = self.old_objective[0]*10 + (self.new_objective[0]-self.old_objective[0])*10*self.progress
        y = self.old_objective[1]*10 + (self.new_objective[1]-self.old_objective[1])*10*self.progress

        self.position = [x, y]

    def draw(self, sm: ScreenManager):
        sm.part_pixel_blit(self.position[0], self.position[1], self.texture_name)
