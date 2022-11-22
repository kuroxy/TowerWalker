import math

from ScreenManager import ScreenManager


class Turret:
    def __init__(self, turret_id: int, position: list[int, int], t_range: float, damage: float, fire_rate: float, hardness: float, td, texture_name, laser_sound):
        self.turret_id = turret_id

        # --- turret stats ---
        self.position = position
        self.t_range = t_range
        self.damage = damage
        self.fire_rate = fire_rate
        self.fire_timer = self.fire_rate
        self.current_target = None

        self.hardness = hardness
        self.texture_name = texture_name
        # --- utility ---
        self.td = td

        # --- drawing ---
        self.laser_line = None
        self.laser_thickness = 3
        self.laser_color = (0, 255, 0)
        self.laser_show_time = .2  # seconds
        self.laser_draw_timer = 0
        self.laser_sound = laser_sound

    def set_drawing_vars(self, laser_thickness, color, laser_show_time):
        self.laser_thickness = laser_thickness
        self.laser_color = color
        self.laser_show_time = laser_show_time  # seconds

    def update(self, dt: float, sound_m):
        self.fire_timer -= dt
        self.laser_draw_timer -= dt

        if self.fire_timer <= 0:
            self.shoot(sound_m)

    def shoot(self, sound_m):
        if self.current_target not in self.td.enemies or self.current_target is None:
            self.select_target()
            return

        x_diff = (self.current_target.position[0]-self.position[0])
        y_diff = (self.current_target.position[1]-self.position[1])
        if x_diff**2 + y_diff**2 > self.t_range**2:
            self.select_target()
            return

        # allowed to shoot
        self.fire_timer = self.fire_rate

        self.current_target.health -= self.damage

        # drawing
        sound_m.play_sound(self.laser_sound)
        self.laser_line = [self.position[0]+9, self.position[1], self.current_target.position[0]+5, self.current_target.position[1]+5]
        self.laser_draw_timer = self.laser_show_time

    def select_target(self):
        closest = None
        distance_nn = math.inf

        for enemy in self.td.enemies:
            x_diff = (enemy.position[0] - self.position[0])
            y_diff = (enemy.position[1] - self.position[1])
            dis_nn = x_diff**2 + y_diff**2
            if dis_nn < distance_nn and dis_nn < self.t_range**2:
                closest = enemy
                distance_nn = dis_nn

        self.current_target = closest

    def draw(self, sm: ScreenManager):
        if self.laser_draw_timer > 0:
            sm.pixel_line(self.laser_color, self.laser_line, self.laser_thickness)

    def copy(self):
        cop = Turret(self.turret_id, self.position, self.t_range, self.damage, self.fire_rate, self.hardness, self.td, self.texture_name, self.laser_sound)
        cop.set_drawing_vars(self.laser_thickness, self.laser_color, self.laser_show_time)
        return cop
