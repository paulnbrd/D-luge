import numpy as np
from functools import lru_cache
import pygame
from dataclasses import dataclass


pygame.init()
with open("./etopo5.dat", "rb") as data:
    etopo = np.fromfile(data, dtype='>i2').reshape((2160, 4320))

# Make lines columns and columns lines
etopo = etopo.T

# Deep etopo copy
default_etopo = etopo.copy()

print("* {} nombres de points topographiques".format(etopo.size))


def bgrtoint32(rgb):
    color = 0
    for c in rgb[::-1]:
        color = (color << 8) + c
        # Do not forget parenthesis.
        # color<< 8 + c is equivalent of color << (8+c)
    return color


@lru_cache(maxsize=None)
def make_color(
    topo_value: float,
):
    # Pygame utilise BGR
    rgb = _make_color(topo_value)
    bgr = (rgb[2], rgb[1], rgb[0])
    return bgrtoint32(bgr)


@lru_cache(maxsize=None)
def _make_color(topo_value: float):
    if topo_value < -8000:
        return np.array([0, 0, 0])
    elif topo_value < 0:
        return np.array([0, 0, round(255 + topo_value * 255 / 8000)])
    elif topo_value < 1000:
        return np.array([40, round(127 + topo_value * 128 / 1000), 0])
    elif topo_value < 2000:
        return np.array([round(80 + (topo_value - 1000) * 80 / 1000), 255, 0])
    elif topo_value < 3000:
        return np.array([round(160 + (topo_value - 2000) * 95 / 1000), 255, 0])
    elif topo_value < 4000:
        return np.array([round(255 - (topo_value - 3000) * 128 / 1000), round(255 - (topo_value - 3000) * 255 / 1000), 50])
    elif topo_value < 5000:
        return np.array([128, 128, 128])
    else:
        return np.array([250, 250, 250])


v_make_color = np.vectorize(make_color, otypes=[int])


@lru_cache(maxsize=None)
def bake_for_offset(
    offset: float = 0,
    from_x: int = 0,
    from_y: int = 0,
    to_x: int = 4320,
    to_y: int = 2160,
    scale: float = 1,
):

    # On cherche à ramener les coordonnées sur la carte
    # du centre de l'écran

    original = default_etopo[::scale, ::scale]
    from_a = original

    while from_x < 0:
        from_x += len(original)
        to_x += len(original)
        from_a = np.concatenate((from_a, original), axis=0)
    while to_x > len(from_a):
        from_a = np.concatenate((from_a, original), axis=0)
    original = from_a
    while from_y < 0:
        from_y += len(original[0])
        to_y += len(original[0])
        from_a = np.concatenate((from_a, original), axis=1)
    while to_y > len(from_a[0]):
        from_a = np.concatenate((from_a, original), axis=1)

    # print("From X: {} To X: {} From Y: {} To Y: {}".format(
    #     from_x, to_x, from_y, to_y))
    from_a = from_a[from_x:to_x, from_y:to_y]

    c = from_a.copy()
    c[c < offset] -= offset
    etopo = v_make_color(c)
    return etopo


cache = {}


@dataclass
class MapPosition:
    x: int
    y: int
    width: int
    height: int
    offset: float

    # 1 = 1 point par pixel, 2 = 1 point pour 2 pixels, ...
    resolution: int = 1
    scale: float = 4

    def bake(self):

        params = (self.offset, self.x, self.y, self.width,
                  self.height, self.scale, self.resolution)

        if params in cache:
            return cache[params]

        result = bake_for_offset(
            offset=self.offset,
            from_x=self.x,
            from_y=self.y,
            to_x=round(self.x + (self.width * self.scale) // self.resolution),
            to_y=round(self.y + (self.height * self.scale) // self.resolution),
            scale=self.resolution,
        )

        # Mise à l'échelle, en fonction de la résolution
        # Ex: resolution = 5, on duplique 5 fois chaque pixel
        # On fait donc un zoom x5
        result = np.repeat(result, self.resolution, axis=0)
        result = np.repeat(result, self.resolution, axis=1)

        inverse = round(1/self.scale)
        if inverse > 1:
            result = np.repeat(result, inverse, axis=0)
            result = np.repeat(result, inverse, axis=1)
        else:
            result = result[::round(self.scale), ::round(self.scale)]

        # print(result.shape)

        cache[params] = result
        return result
