import pygame as pg

from robot import Robot

WIN_SIZE = WIN_WIDTH, WIN_HEIGHT = 900, 900


class Simulation:
    def __init__(self) -> None:
        self.running: bool = False
        self.dt: float = 1
        self.surface: pg.Surface = pg.display.set_mode(WIN_SIZE)
        self.image: pg.Surface = pg.image.load("1.png")
        self.robot: Robot = Robot(self, 20, (100, 100), 100)

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
