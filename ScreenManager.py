import pygame


class ScreenManager:
    def __init__(self, window_size: list[int, int], pixel_size: int, screen_surface: pygame.Surface):
        self.window_size = window_size
        self.pixel_size = pixel_size
        self.screen_surface = screen_surface

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
        self.screen_surface.blit(self.scaled_textures[texture_name], [int(x)*self.pixel_size, int(y)*self.pixel_size])

    def part_pixel_blit(self, x: float, y: float, texture_name: str):
        self.screen_surface.blit(self.scaled_textures[texture_name], [int(x*self.pixel_size), int(y*self.pixel_size)])

    def absolute_pixel_blit(self, x: int, y: int, texture_name: str):
        self.screen_surface.blit(self.scaled_textures[texture_name], [int(x), int(y)])

    def pixel_text_blit(self, x: int, y: int, text: str, size: int, color: tuple[int, int, int]):
        font = pygame.font.SysFont('arial', size*self.pixel_size)
        rendered_text = font.render(text, True, color)
        self.screen_surface.blit(rendered_text, (x*self.pixel_size, y*self.pixel_size))

    def fill(self, color: tuple[int, int, int]):
        self.screen_surface.fill(color)

    def screen_to_pixel(self, position: tuple[int, int]) -> list[int, int]:
        return [int(position[0] / self.pixel_size), int(position[1] / self.pixel_size)]

    def pixel_line(self, color, line, width):
        pygame.draw.line(self.screen_surface, color, [line[0]*self.pixel_size, line[1]*self.pixel_size],[line[2]*self.pixel_size, line[3]*self.pixel_size], width)

    def pixel_micro_font(self, x, y, text, color):
        if not self.micro_font:
            return
        rendered_text = self.micro_font.render(text, True, color)
        self.screen_surface.blit(rendered_text, (x*self.pixel_size, y*self.pixel_size))