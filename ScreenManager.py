import pygame


class ScreenManager:
    def __init__(self, window_size: list[int, int], pixel_size: int, screen_surface: pygame.Surface):
        self.window_size = window_size
        self.pixel_size = pixel_size
        self.screen_surface = screen_surface

        self.pixel_surface = pygame.Surface([int(self.window_size[0]/self.pixel_size), int(self.window_size[1]/self.pixel_size)])
        self.pixel_surface.set_colorkey((0, 0, 0))

        self.fill_surface = pygame.Surface([int(self.window_size[0]), int(self.window_size[1])], pygame.SRCALPHA)

        self.textures = {}
        self.scaled_textures = {}

        self.micro_font_size = 6
        self.micro_font = None

    def load_micro_font(self, location):
        self.micro_font = pygame.font.Font(location, 5*self.pixel_size)

    def load_pixel_texture(self, directory: str, name: str, transparent: bool):
        texture = pygame.image.load(directory)
        if transparent:
            texture = texture.convert_alpha()
        else:
            texture = texture.convert()

        self.textures[name.lower()] = texture
        new_size = texture.get_size()
        new_size = [new_size[0]*self.pixel_size, new_size[1]*self.pixel_size]
        self.scaled_textures[name.lower()] = pygame.transform.scale(texture, new_size)

    def pixel_blit(self, x: int, y: int, texture_name: str):
        self.screen_surface.blit(self.scaled_textures[texture_name.lower()], [int(x)*self.pixel_size, int(y)*self.pixel_size])

    def part_pixel_blit(self, x: float, y: float, texture_name: str):
        self.screen_surface.blit(self.scaled_textures[texture_name.lower()], [int(x*self.pixel_size), int(y*self.pixel_size)])

    def absolute_pixel_blit(self, x: int, y: int, texture_name: str):
        self.screen_surface.blit(self.scaled_textures[texture_name.lower()], [int(x), int(y)])

    def pixel_text_blit(self, x: int, y: int, text: str, size: int, color: tuple[int, int, int]):
        font = pygame.font.SysFont('arial', size*self.pixel_size)
        rendered_text = font.render(text, True, color)
        self.screen_surface.blit(rendered_text, (x*self.pixel_size, y*self.pixel_size))

    def fill(self, color: tuple[int, int, int]):
        self.screen_surface.fill(color)

    def fill_with_opacity(self, color: tuple[int, int, int], opacity: int):
        self.fill_surface.fill([color[0], color[1], color[2], opacity])
        self.screen_surface.blit(self.fill_surface, [0, 0])

    def screen_to_pixel(self, position: tuple[int, int]) -> list[int, int]:
        return [int(position[0] / self.pixel_size), int(position[1] / self.pixel_size)]

    def pixel_line(self, color, line, width):
        self.pixel_surface.fill((0, 0, 0))
        pygame.draw.line(self.pixel_surface, color, [line[0], line[1]], [line[2], line[3]], width)
        surf = pygame.transform.scale(self.pixel_surface, self.window_size)
        self.screen_surface.blit(surf, (0, 0))

    def pixel_micro_font(self, x, y, text, color):
        if not self.micro_font:
            return
        rendered_text = self.micro_font.render(text, True, color)
        self.screen_surface.blit(rendered_text, (x*self.pixel_size, y*self.pixel_size))

    def normal_micro_font(self, x, y, text, color):
        if not self.micro_font:
            return
        rendered_text = self.micro_font.render(text, True, color)
        self.screen_surface.blit(rendered_text, (x, y))