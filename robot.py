from __future__ import annotations

import math
from typing import TYPE_CHECKING, Tuple

from constants import EXTRA_COLLISION

if TYPE_CHECKING:
    from simulation import Simulation
import pygame as pg
from enum import Enum

from util import line_end, dx_dy, distance
from scanner import Scanner, Point


class Robot:
    class Action(Enum):
        POST_INIT = "POST_INIT"
        GO_TO_WALL = "GO_TO_WALL"
        GO_ALONG_WALL = "GO_ALONG_WALL"

    def __init__(self, simulation: Simulation, radius: float, position: Tuple[float, float], speed: float) -> None:
        self.simulation: Simulation = simulation
        self.radius: float = radius
        self.position: Tuple[float, float] = position
        self.speed: float = speed
        self.radians: float = 0

        self.action: Robot.Action = Robot.Action.POST_INIT
        self.closest_line = ...

        self.scanner: Scanner = Scanner(self.simulation)

    def update(self) -> None:
        self.scanner.scan()
        self.logics()

    def logics(self) -> None:
        match self.action:
            case Robot.Action.POST_INIT:
                closest_point = self.scanner.points_index.get_closest(*self.position)
                for line in self.scanner.result_lines:
                    if line.point_right == closest_point or line.point_left == closest_point:
                        self.closest_line = line
                        self.action = Robot.Action.GO_TO_WALL
                        break

            case Robot.Action.GO_TO_WALL:
                pg.draw.line(self.simulation.surface, (255, 0, 0), self.closest_line.point_left.position,
                             self.closest_line.point_right.position, 5)

                perpendicular_slope = -1 / self.closest_line.slope
                perpendicular_radians = math.atan(perpendicular_slope) - math.pi / 2
                self.radians = perpendicular_radians
                will_collide = self.move_forward()
                if will_collide:
                    self.radians = self.closest_line.radians + math.pi / 2
                    self.action = Robot.Action.GO_ALONG_WALL

            case Robot.Action.GO_ALONG_WALL:
                collision = self.move_forward()
                if collision:
                    self.radians += math.pi / 2

    def move_forward(self) -> bool:
        dx, dy = dx_dy(self.speed, self.radians)
        position = self.position[0] + dx, self.position[1] + dy
        if distance(*self.scanner.points_index.get_closest(*position).position, *position) < self.radius:
            return True
        self.position = position
        return False

    def draw(self) -> None:
        pg.draw.circle(self.simulation.surface, (255, 255, 0), self.position, self.radius, 2)
        pg.draw.line(self.simulation.surface, (255, 255, 255), self.position,
                     line_end(*self.position, self.radius, self.radians))

        # self.scanner.draw_dots()
        self.scanner.draw_lines()
