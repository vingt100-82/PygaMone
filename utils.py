from typing import Dict, List, Any, Tuple, Optional, Union, TypeVar
import time
import pygame
import game_error as err
import game
import pokemon.pokemon_type as pokemon_type
import pokemon.player_pokemon as player_pokemon
import main
import numpy as np


def force():
    pass


def get_part_i(image: pygame.Surface, coord: Tuple[float, float, float, float],
               transform: Tuple[int, int] = (0, 0), flip: Tuple[bool, bool] = (False, False)) -> pygame.Surface:
    s = pygame.Surface((coord[2] - coord[0], coord[3] - coord[1]), pygame.SRCALPHA)
    s.blit(image, (0, 0), pygame.Rect(coord))
    if transform != (0, 0):
        copy_transform = [transform[0], transform[1]]
        if copy_transform[0] == -1:
            copy_transform[0] = coord[2] - coord[0]
        if copy_transform[1] == -1:
            copy_transform[1] = coord[3] - coord[1]
        transform = int(copy_transform[0]), int(copy_transform[1])
        s = pygame.transform.scale(s, transform)
    if flip != (False, False):
        s = pygame.transform.flip(s, flip[0], flip[1])
    return s


MENU_IMAGE = pygame.image.load("assets/textures/hud/menu.png")
ARROW = get_part_i(MENU_IMAGE, (0, 64, 22, 91))
RED_POKEBALL = get_part_i(MENU_IMAGE, (32, 91, 64, 123))
GRAY_POKEBALL = get_part_i(MENU_IMAGE, (0, 91, 32, 123))
POINT_POKEBALL = get_part_i(MENU_IMAGE, (64, 91, 96, 123))


def current_milli_time() -> int:
    return int(round(time.time() * 1000))


def time_to_string(t: int) -> str:
    hours = t // (60 * 60)
    t -= hours * (60 * 60)
    minutes = t // 60
    t -= minutes * 60
    return str(hours) + ":" + ("0" if minutes < 9 else "") + str(minutes)


def draw_select_box(display: pygame.Surface, _x: float, _y: float,
                    text: List[Tuple[pygame.Surface, pygame.Surface]],
                    selected: int, width: int = 100,
                    over_color=(0, 0, 0), bg_color=(255, 255, 255), bg_border=(100, 100, 100)):

    _h = 20 + 28 * len(text)

    pygame.draw.rect(display, bg_color, pygame.Rect(_x, _y, width, _h), border_radius=10)
    pygame.draw.rect(display, bg_border, pygame.Rect(_x - 1, _y - 1, width + 1, _h + 1), border_radius=10, width=1)
    _y += 10
    _x += 10
    for i in range(len(text)):
        if selected == i:
            draw_rond_rectangle(display, _x + 5, _y, 20, width - 30, over_color)
        _text = text[i][1 if selected == i else 0]
        display.blit(_text, (_x, _y))
        _y += 28


def draw_rond_rectangle(display: pygame.Surface, _x: float, _y: float,
                        height: float, width: float, color: Tuple[int, int, int]):
    height *= 0.5
    pygame.draw.circle(display, color, (_x, _y + height), height)
    pygame.draw.circle(display, color, (_x + width, _y + height), height)
    pygame.draw.rect(display, color, pygame.Rect(_x, _y, width, height * 2))


# R = TypeVar('R', pygame.Rect, pygame.RectType, tuple[int, int, int, int])

def draw_split_rectangle(display: pygame.Surface, rect: tuple[int, int, int, int], split_up: float, split_down: float,
                              color: Union[tuple[int, int, int], str], color_2: Union[tuple[int, int, int], str]):
    pygame.draw.rect(display, color, rect)
    poly = (
        (rect[0] + rect[2] * split_up, rect[1]),
        (rect[0] + rect[2], rect[1]),
        (rect[0] + rect[2], rect[1] + rect[3] - 1),
        (rect[0] + rect[2] * split_down, rect[1] + rect[3] - 1),
    )
    pygame.draw.polygon(display, color_2, poly)


def draw_split_rond_rectangle(display: pygame.Surface, rect: tuple[int, int, int, int], split_up: float, split_down: float,
                              color: Union[tuple[int, int, int], str], color_2: Union[tuple[int, int, int], str]):
    height = rect[3] * 0.5
    pygame.draw.circle(display, color, (rect[0], rect[1] + height), height)
    pygame.draw.circle(display, color_2, (rect[0] + rect[2], rect[1] + height), height)
    draw_split_rectangle(display, rect, split_up, split_down, color, color_2)


def get_args(data: Dict[str, Any], key: str, _id: Any, default=None, type_check=None, _type="pokmon") -> Any:
    value = None
    if default is not None:
        value = data[key] if key in data else None if default == "NONE" else default
    else:
        if key not in data:
            raise err.PokemonParseError("No {} value for a {} ({}) !".format(key, _type, _id))
        value = data[key]
    if type_check:
        if value and not isinstance(value, type_check):
            raise err.PokemonParseError(
                "Invalid var type for {} need be {} for {} ({})".format(key, type_check, _type, _id))
    return value


def draw_type(display: pygame.Surface, _x: float, _y: float, _type: 'pokemon_type.Type'):
    pygame.draw.rect(display, (0, 0, 0), pygame.Rect(_x, _y, 85, 16),
                     border_radius=2)
    display.blit(_type.image, (_x, _y))
    display.blit(game.FONT_16.render(_type.get_name().upper(), True, (255, 255, 255)), (_x + 26, _y + 1))


def draw_ability(display: pygame.Surface, coord: Tuple[float, float], p_ability: 'player_pokemon.PokemonAbility'):
    draw_split_rond_rectangle(display, (coord[0], coord[1], main.SCREEN_SIZE[0] * 0.2, 34), 0.85, 0.8, (255, 255, 255), (70, 68, 69))
    # draw_rond_rectangle(display, coord[0] + main.SCREEN_SIZE[0] * 0.18, coord[1], 34, 40, (70, 68, 69))
    display.blit(game.FONT_20.render(p_ability.ability.get_name() if p_ability else "-------------", True, (0, 0, 0)),
                 (coord[0] + 5, coord[1] + 6))
    if p_ability:
        draw_type(display, coord[0] + main.SCREEN_SIZE[0] * 0.10, coord[1] + 8,  p_ability.ability.type)

    pp = "{}/{}".format(p_ability.pp, p_ability.max_pp) if p_ability else "--/--"
    move = game.FONT_SIZE_20[0] * (1.8 if not p_ability else (2.5 if p_ability.pp > 9 else 1.5))
    display.blit(game.FONT_20.render(pp, True, (255, 255, 255)),
                 (coord[0] + main.SCREEN_SIZE[0] * 0.19 - move, coord[1] + 6))
    pass


def draw_ability_2(display: pygame.Surface, coord: Tuple[float, float],
                   p_ability: 'player_pokemon.PokemonAbility', border: bool = False):
    type_color = p_ability.ability.type.image.get_at((0, 0)) if p_ability else (255, 255, 255)
    if border:
        draw_rond_rectangle(display, coord[0] - 3, coord[1] - 3, 46, 226, (0, 0, 0))
    draw_rond_rectangle(display, coord[0], coord[1], 40, 220, type_color)
    draw_rond_rectangle(display, coord[0] + 180, coord[1], 40, 40, (0, 0, 0))
    if p_ability:
        display.blit(pygame.transform.scale(p_ability.ability.type.image, (44, 32)), (coord[0] - 10, coord[1] + 4), pygame.Rect(0, 0, 32, 32))

    display.blit(game.FONT_20.render(p_ability.ability.get_name() if p_ability else "-------------", True, (0, 0, 0)),
                 (coord[0] + 23, coord[1] + 8))
    pp = "{}/{}".format(p_ability.pp, p_ability.max_pp) if p_ability else "--/--"
    move = game.FONT_SIZE_24[0] * (1.8 if not p_ability else (2.5 if p_ability.pp > 9 else 1.5))
    display.blit(game.FONT_24.render(pp, True, (255, 255, 255) if p_ability is None or p_ability.pp > 0 else (166, 26, 2)),
                 (coord[0] + 193 - move, coord[1] + 6))


def draw_progress_bar(display: pygame.Surface, coord: Tuple[float, float], size: Tuple[float, float],
                      bg_color: Tuple[int, int, int], color: Tuple[int, int, int], progress: float):

    pygame.draw.rect(display, bg_color, pygame.Rect(coord[0], coord[1], size[0], size[1]))
    pygame.draw.rect(display, color, pygame.Rect(coord[0], coord[1], size[0] * progress, size[1]))


def min_max(min_v: int, value: int, max_v: int) -> int:
    return min_v if value < min_v else max_v if value > max_v else value

def hexa_color_to_rgb(hexa: str) -> Tuple[int, int, int]:
    if hexa[0] == '#':
        hexa = hexa[1:]
    return int('0x' + hexa[0:2], 16), int('0x' + hexa[2:4], 16), int('0x' + hexa[4:6], 16)


def change_image_color(surface: pygame.Surface, color: tuple[int, int, int]) -> pygame.Surface:
    size = surface.get_size()
    for x in range(size[0]):
        for y in range(size[1]):
            px = surface.get_at((x, y))
            if px[3] != 0:
                surface.set_at((x, y), color)
    return surface


def color_image(surface: pygame.Surface, color: Union[tuple[int, int, int], tuple[int, int, int, int]]) -> pygame.Surface:
    alpha = (100 if len(color) == 3 else color[3]) / 255
    size = surface.get_size()
    for x in range(size[0]):
        for y in range(size[1]):
            px = surface.get_at((x, y))
            if px[3] != 0:
                al = (1 - alpha)
                f_px = (
                    int(color[0] * alpha + px[0] * al),
                    int(color[1] * alpha + px[1] * al),
                    int(color[2] * alpha + px[2] * al)
                )
                surface.set_at((x, y), f_px)
    return surface


def get_first_color(surface: pygame.Surface) -> Tuple[int, int]:

    size = surface.get_size()

    def _y_():
        for y_ in range(size[1] - 1, -1, -1):
            for x_ in range(size[0] - 1, -1, -1):
                if surface.get_at((x_, y_))[3] != 0:
                    return y_
        return 0

    def _x_():
        for x_ in range(size[0] - 1, -1, -1):
            for y_ in range(size[1] - 1, -1, -1):
                if surface.get_at((x_, y_))[3] != 0:
                    return x_
        return 0

    x = _x_()
    y = _y_()
    return x, y


GAMEPAD_KEYS = [
    'A', 'B', 'X', 'Y', 'L1', 'R1', '-', '+', 'R', 'L', '?', '\u2191', '\u2193', '`\u2190', '\u2191'
]


def remove_holes(surface, background=(0, 0, 0)):
    """
    Removes holes caused by aliasing.

    The function locates pixels of color 'background' that are surrounded by pixels of different colors and set them to
    the average of their neighbours. Won't fix pixels with 2 or less adjacent pixels.

    Args:
        surface (pygame.Surface): the pygame.Surface to anti-aliasing.
        background (3 element list or tuple): the color of the holes.

    Returns:
        anti-aliased pygame.Surface.
    """
    width, height = surface.get_size()
    array = pygame.surfarray.array3d(surface)
    contains_background = (array == background).all(axis=2)

    neighbours = (0, 1), (0, -1), (1, 0), (-1, 0)

    for row in range(1, height-1):
        for col in range(1, width-1):
            if contains_background[row, col]:
                average = np.zeros(shape=(1, 3), dtype=np.uint16)
                elements = 0
                for y, x in neighbours:
                    if not contains_background[row+y, col+x]:
                        elements += 1
                        average += array[row+y, col+x]
                if elements > 2:  # Only apply average if more than 2 neighbours is not of background color.
                    array[row, col] = average // elements

    return pygame.surfarray.make_surface(array)


def draw_arrow(display: pygame.Surface, up: bool, x, y, color, size=1):
    l = 10 * size
    h = 5 * size
    x -= l // 2
    p = (x, y), (x + l, y), (x + l // 2, (y - h) if up else (y + h))
    pygame.draw.polygon(display, color, p)


def get_center(surface: pygame.Surface, rec: tuple[int, int, int, int], center_x=True, center_y=True) -> tuple[int, int]:
    size = surface.get_size()
    x = rec[0] + rec[2] // 2 - size[0] // 2 if center_x else rec[0]
    y = rec[1] + rec[3] // 2 - size[1] // 2 if center_y else rec[1]
    return x, y


def draw_button_info(surface: pygame.Surface, **keys):
    pygame.draw.polygon(surface, "#000000", ((0, 570), (1060, 570), (1060, 600), (0, 600)))
    x = 1040
    h = 30
    c_y = 600 - h / 2
    y = int(c_y - game.FONT_SIZE_20[1] / 2)
    is_board = game.get_game_instance().last_input_type == game.INPUT_TYPE_KEYBOARD == 0
    for name, key in keys.items():
        key_char = (pygame.key.name(key[0]) if is_board else GAMEPAD_KEYS[key[2]]).upper()
        txt = game.FONT_20.render(name, True, (255, 255, 255))
        x -= txt.get_size()[0]
        surface.blit(txt, (x, y))
        mt_char = len(key_char) > 1
        font = game.FONT_20 if mt_char else game.FONT_24
        key = font.render(key_char, True, (0, 0, 0))
        size = key.get_size()
        if mt_char:
            w = size[0]
            x -= w + 15
            draw_rond_rectangle(surface, x, 600 - h + 4, h - 8, w, (255, 255, 255))
            surface.blit(key, (x, y))
            x -= 20
        else:
            x -= h // 2 + 2
            pygame.draw.circle(surface, (255, 255, 255), (x, c_y), h // 2 - 2)
            surface.blit(key, (x - size[0] // 2, c_y - size[1] // 2))
            x -= h // 2 + 2