from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from simulation import Simulation
import pygame as pg

from util import line_end
from scanner import Scanner


class Robot:
    def __init__(self, simulation: Simulation, radius: float, position: Tuple[float, float], speed: float) -> None:
        self.simulation: Simulation = simulation
        self.radius: float = radius
        self.position: Tuple[float, float] = position
        self.speed: float = speed
        self.radians: float = 0

        self.scanner: Scanner = Scanner(self.simulation)

    def update(self) -> None:
        self.scanner.scan()

    def draw(self) -> None:
        pg.draw.circle(self.simulation.surface, (255, 255, 0), self.position, self.radius, 2)
        pg.draw.line(self.simulation.surface, (255, 255, 255), self.position,
                     line_end(*self.position, self.radius, self.radians))

        # self.scanner.draw_dots()
        self.scanner.draw_lines()
