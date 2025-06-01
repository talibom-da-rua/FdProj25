from graphics import *
from time import sleep

class Waiter:
    def __init__(self, win, start_pos):

        self.win = win
        self.pos = Point(*start_pos)
        self.start_pos = Point(*start_pos)
        self.shape = Circle(self.pos, 4)
        self.shape.setFill("red")
        self.shape.draw(win)

    def move_to(self, destino):
        dx = (destino.getX() - self.pos.getX()) / 100
        dy = (destino.getY() - self.pos.getY()) / 100

        for _ in range(100):
            self.shape.move(dx, dy)
            self.pos.move(dx, dy)
            sleep(0.01)

    def voltar(self):
        dx = (self.start_pos.getX() - self.pos.getX()) / 100
        dy = (self.start_pos.getY() - self.pos.getY()) / 100

        for _ in range(100):
            self.shape.move(dx, dy)
            self.pos.move(dx, dy)
            sleep(0.01)
