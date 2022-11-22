import pygame


class SoundManager:
    NEXT_SONG = pygame.USEREVENT + 1

    def __init__(self):
        self.sounds = {}
        self.music = []
        self.current_music_track = 0

    def load_sound(self, name, path):
        self.sounds[name.lower()] = pygame.mixer.Sound(path)

    def load_music(self, path):
        self.music.append(path)

    def play_sound(self, sound_name):
        self.sounds[sound_name.lower()].play()

    def play_next_track(self):
        pygame.mixer.music.load(self.music[self.current_music_track])
        pygame.mixer.music.play()
        self.current_music_track += 1
        self.current_music_track %= len(self.music)
        # send event NEXT every time tracks ends
        pygame.mixer.music.set_endevent(SoundManager.NEXT_SONG)

    def play_random_track(self):
        pygame.mixer.music.load(random.choice(self.music))
        pygame.mixer.music.play()
        # send event NEXT every time tracks ends
        pygame.mixer.music.set_endevent(SoundManager.NEXT_SONG)

    def set_music_volume(self, volume: float):
        pygame.mixer.music.set_volume(volume)

    def pause_music(self):
        pygame.mixer.music.pause()

    def unpause_music(self):
        pygame.mixer.music.unpause()