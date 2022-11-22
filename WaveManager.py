import random


class WaveManager:
    def __init__(self, td, enemy_list):
        self.td = td

        self.wave_number = 0

        self.wave_spawn_monster_list = []
        self.spawn_speed = .5
        self.spawn_timer = self.spawn_speed

        self.time_between_waves = 10
        self.time_between_waves_timer = self.time_between_waves

        self.enemies = enemy_list  # cost, health, speed, damage, value, texture_name
        # --- enemies ---
        # self.enemies.append([1, 50, 3, 2, 1, "skeleton"])
        # self.enemies.append([3, 200, 1, 2, 2, "arrows"])

    def update(self, dt):

        if len(self.wave_spawn_monster_list) > 0:  # still monsters to spawn
            self.spawn_timer -= dt

            if self.spawn_timer <= 0:
                self.spawn_timer = self.spawn_speed
                enemy_to_add = self.wave_spawn_monster_list.pop()
                self.td.add_enemy(enemy_to_add[1], enemy_to_add[2], enemy_to_add[3], enemy_to_add[4], enemy_to_add[5])

        elif len(self.td.enemies) == 0:
            self.time_between_waves_timer -= dt

            if self.time_between_waves_timer <= 0:
                self.time_between_waves_timer = self.time_between_waves
                self.wave_number += 1
                self.wave_spawn_monster_list = self.generate_new_wave(self.wave_number)

    def generate_new_wave(self, wave_number):
        monster_spawn_currency = round(.4*pow(wave_number, 1.4)+1)
        monster_spawn_list = []
        while monster_spawn_currency > 0:
            random_monster = random.choice(self.get_monster_list(monster_spawn_currency))
            monster_spawn_currency -= random_monster[0]
            monster_spawn_list.append(random_monster)
        return monster_spawn_list

    def get_monster_list(self, value):
        """ returns the list where the enemy costs are less then the value
        :param value: max cost of monster
        """
        return_list = []
        for i in self.enemies:
            if i[0] <= value:
                return_list.append(i)
        return return_list

    def reset(self):
        self.wave_number = 0
        self.wave_spawn_monster_list = []
