import random

from Enemy import Enemy


class WaveManager:
    def __init__(self, td, enemy_list):
        self.td = td

        self.wave_number = 0

        self.wave_spawn_monster_list = []
        self.spawn_speed = .5
        self.spawn_timer = self.spawn_speed

        self.time_between_waves = 10
        self.time_between_waves_timer = self.time_between_waves

        self.enemies = enemy_list  # texture_name, cost, health, speed, damage, value,
        # --- enemies ---
        # self.enemies.append([1, 50, 3, 2, 1, "skeleton"])
        # self.enemies.append([3, 200, 1, 2, 2, "arrows"])

        self.reset()

    def update(self, dt):

        if len(self.wave_spawn_monster_list) > 0:  # still monsters to spawn
            self.spawn_timer -= dt

            if self.spawn_timer <= 0:
                self.spawn_timer = self.spawn_speed
                enemy_to_add = self.wave_spawn_monster_list.pop()
                self.spawn_enemy(enemy_to_add, self.wave_number)

        elif len(self.td.enemies) == 0:
            self.time_between_waves_timer -= dt

            if self.time_between_waves_timer <= 0:
                self.time_between_waves_timer = self.time_between_waves
                self.wave_number += 1
                self.wave_spawn_monster_list = self.generate_new_wave(self.wave_number)

    def spawn_enemy(self, enemy_from_list: list, wave: int):
        health = enemy_from_list[2]
        speed = enemy_from_list[3]
        damage = enemy_from_list[4]
        value = enemy_from_list[5]
        if wave >= enemy_from_list[6]:
            scale_amount = (wave-enemy_from_list[6])
            health += scale_amount * enemy_from_list[7]
            speed += scale_amount * enemy_from_list[8]
            damage += scale_amount * enemy_from_list[9]

        if enemy_from_list[10] != -1:
            health = min(health, enemy_from_list[10])

        if enemy_from_list[11] != -1:
            speed = min(speed, enemy_from_list[11])

        if enemy_from_list[12] != -1:
            damage = min(damage, enemy_from_list[12])
        health += (random.random() - .5) * .1 * health
        speed += (random.random() - .5) * .1 * speed
        damage += (random.random() - .5) * .1 * damage

        print(f"Spawned enemy ({round(health,2)}, {round(speed,2)}, {round(damage,2)})")
        enemy = Enemy(self.td.map, self.td.spawner_pos[0], self.td.spawner_pos[1], enemy_from_list[0])
        enemy.set_enemy_stats(enemy_from_list[0], health, speed, damage, value)
        self.td.add_enemy(enemy)

    def generate_new_wave(self, wave_number):
        self.spawn_speed = max(.05, self.spawn_speed-.009)
        monster_spawn_currency = round(.4*pow(wave_number, 1.4)+1)
        monster_spawn_list = []
        while monster_spawn_currency > 0:
            random_monster = random.choice(self.get_monster_list(monster_spawn_currency))
            monster_spawn_currency -= random_monster[1]
            monster_spawn_list.append(random_monster)
        return monster_spawn_list

    def get_monster_list(self, value):
        """ returns the list where the enemy costs are less then the value
        :param value: max cost of monster
        """
        return_list = []
        for i in self.enemies:
            if i[1] <= value:
                return_list.append(i)
        return return_list

    def reset(self):
        self.wave_number = 0
        self.spawn_speed = .65
        self.spawn_timer = self.spawn_speed
        self.wave_spawn_monster_list = []
