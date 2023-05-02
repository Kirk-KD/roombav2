import pygame as pg

from robot import Robot
from constants import WIN_SIZE


class Simulation:
    def __init__(self) -> None:
        self.running: bool = False
        self.dt: float = 1
        self.surface: pg.Surface = pg.display.set_mode(WIN_SIZE)
        self.image: pg.Surface = pg.transform.scale(pg.image.load("room.png"), WIN_SIZE)
        self.robot: Robot = Robot(self, 15, (250, 300), 2)

    def __frame(self) -> None:
        self.surface.blit(self.image, (0, 0))

        self.robot.update()
        self.robot.draw()

    def __events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

    def run(self) -> None:
        self.running = True

        while self.running:
            self.__events()
            self.__frame()
            pg.display.flip()
