from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Tuple
if TYPE_CHECKING:
    from simulation import Simulation
from constants import WIN_WIDTH, WIN_HEIGHT

import pygame as pg

from util import dx_dy, distance


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.position: Tuple[float, float] = self.x, self.y

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y


class Line:
    def __init__(self, point1: Point, point2: Point) -> None:
        self.point_left: Point = min(point1, point2, key=lambda p: p.x)
        self.point_right: Point = max(point1, point2, key=lambda p: p.x)
        if self.point_right.x - self.point_left.x == 0:
            self.slope: float = float("inf")
        else:
            self.slope: float = (self.point_right.y - self.point_left.y) / (self.point_right.x - self.point_left.x)
        self.radians: float = math.atan(self.slope) if self.slope != float("inf") else math.radians(90)
        self.length: float = distance(self.point_left.x, self.point_left.y, self.point_right.x, self.point_right.y)

    def join(self, other: Line) -> Line:
        points = [self.point_left, self.point_right, other.point_left, other.point_right]
        new_lines = []
        for i in range(3):
            for j in range(i + 1, 4):
                new_lines.append(Line(points[i], points[j]))

        return max(new_lines, key=lambda l: l.length)

    def distance(self, other: Line) -> float:
        ds = [distance(*self.point_left.position, *other.point_left.position),
              distance(*self.point_left.position, *other.point_right.position),
              distance(*self.point_right.position, *other.point_left.position),
              distance(*self.point_right.position, *other.point_right.position)]
        return min(ds)


class Raycast:
    def __init__(self, surface: pg.Surface, max_dist: float, hop_dist: float, color_mask: Tuple[int, int, int]) -> None:
        self.surface: pg.Surface = surface
        self.max_dist: float = max_dist
        self.hop_dist: float = hop_dist
        self.color_mask: Tuple[int, int, int] = color_mask

    def ray(self, starting_position: Tuple[float, float], rad: float) -> Tuple[float, float] | None:
        """
        Cast a ray starting from `starting_position` at an angle of `rad`, in radians.

        :param starting_position: The starting position of the ray
        :param rad: The angle in radians
        :return: The hit point.
        """
        x, y = starting_position
        dx, dy = dx_dy(self.hop_dist, rad)
        dx_small, dy_small = dx_dy(1, rad)

        while (distance(starting_position[0], starting_position[1], x, y) < self.max_dist and
               0 <= x < WIN_WIDTH and 0 <= y < WIN_HEIGHT):
            pixel_x = int(x)
            pixel_y = int(y)
            if self.surface.get_at((pixel_x, pixel_y)) == self.color_mask:
                while pixel_x != starting_position[0] or pixel_y != starting_position[1]:
                    pixel_x = int(x)
                    pixel_y = int(y)
                    if self.surface.get_at((pixel_x, pixel_y)) != self.color_mask:
                        return x, y

                    x -= dx_small
                    y -= dy_small
                return x, y

            x += dx
            y += dy

        return None


class Scanner:
    def __init__(self, simulation: Simulation) -> None:
        self.simulation: Simulation = simulation
        self.raycast: Raycast = Raycast(self.simulation.surface, 300, 5, (255, 255, 255))
        self.result_points: List[Point] = []
        self.result_lines: List[Line] = []

    def too_close(self, point: Point, dist: float) -> bool:
        for p in self.result_points:
            if distance(p.x, p.y, point.x, point.y) <= dist:
                return True

        return False

    def closest_point(self, point: Point, ignore: List[Point] = None) -> Point:
        closest = None
        dist = float("inf")
        for p in self.result_points:
            if p == point or (ignore and p in ignore):
                continue
            d = distance(p.x, p.y, point.x, point.y)
            if d < dist:
                dist = d
                closest = p

        return closest

    def scan(self) -> None:
        self.result_lines = []

        for i in range(0, 360 * 2 + 1):
            deg = i / 2
            xy = self.raycast.ray(self.simulation.robot.position, math.radians(deg))
            if not xy:
                continue
            x, y = xy

            point = Point(x, y)
            if self.too_close(point, 5):
                continue
            self.result_points.append(point)

        visited_points = []
        point = self.result_points[0]
        while len(visited_points) != len(self.result_points) - 1:
            visited_points.append(point)
            closest = self.closest_point(point, visited_points)
            if distance(closest.x, closest.y, point.x, point.y) <= self.simulation.robot.radius:
                self.result_lines.append(Line(point, closest))
            point = closest

        # updated_lines = []
        # current_line = None
        # for i in range(len(self.result_lines)):
        #     line = self.result_lines[i]
        #
        #     if current_line is None:
        #         current_line = line
        #         continue
        #
        #     if abs(line.radians - current_line.radians) <= math.radians(5) and line.distance(current_line) <= 10:
        #         current_line = current_line.join(line)
        #     else:
        #         updated_lines.append(current_line)
        #         current_line = line
        #
        # self.result_lines = updated_lines

    def draw_dots(self) -> None:
        # for point in self.result_points:
        #     pg.draw.circle(self.simulation.surface, (0, 255, 0), point.position, 3)
        ...

    def draw_lines(self) -> None:
        for line in self.result_lines:
            pg.draw.line(self.simulation.surface, (72, 28, 232),
                         line.point_left.position, line.point_right.position, 3)
            pg.draw.circle(self.simulation.surface, (0, 255, 0), line.point_left.position, 2)
            pg.draw.circle(self.simulation.surface, (0, 255, 0), line.point_right.position, 2)
