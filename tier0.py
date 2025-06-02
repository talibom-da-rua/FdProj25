#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 22 18:23:31 2025

@author: stelafernandes
"""

from graphics import GraphWin, Rectangle, Point, Image, Circle, Oval
from time import sleep
from collections import deque

def extrair_categoria_e_numero(nome):
    i = 0
    while i < len(nome) and nome[i].isalpha():
        i += 1
    categoria = nome[:i]
    numero_str = nome[i:]
    numero = int(numero_str) if numero_str.isdigit() else None
    return categoria, numero

def ler_ficheiro_planta(caminho):
    objetos = []
    with open(caminho, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue

            partes = linha.split()
            if len(partes) < 2:
                print(f"Linha ignorada por estar mal formatada: {linha}")
                continue

            nome = partes[0]
            categoria, numero = extrair_categoria_e_numero(nome)
            tipo = partes[1].split('(')[0]

            import re
            pontos_str = ' '.join(partes[1:])
            pontos = re.findall(r'Point\((\d+),(\d+)\)', pontos_str)
            if len(pontos) != 2:
                print(f"Linha ignorada por não ter exatamente 2 pontos: {linha}")
                continue

            p1x, p1y = map(int, pontos[0])
            p2x, p2y = map(int, pontos[1])

            objeto = {
                'nome': nome,
                'categoria': categoria,
                'tipo': tipo,
                'p1': (p1x, p1y),
                'p2': (p2x, p2y)
            }
            objetos.append(objeto)
    return objetos

def desenhar_objetos(objetos, win):
    for obj in objetos:
        p1 = Point(*obj['p1'])
        p2 = Point(*obj['p2'])
        if obj['tipo'] == "Rectangle":
            forma = Rectangle(p1, p2)
        elif obj['tipo'] == "Oval":
            forma = Oval(p1, p2)
        else:
            continue  # Tipo desconhecido
        forma.setFill("lightgrey")
        forma.draw(win)

def is_object(x, y, objetos):
    for obj in objetos:
        x1, y1 = obj['p1']
        x2, y2 = obj['p2']
        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            return obj['categoria'], obj['nome']
    return None, None  # Só identifica

def receive_click(win, objetos):
    while True:
        click_point = win.getMouse()
        x = click_point.getX()
        y = click_point.getY()
        categoria, nome = is_object(x, y, objetos)
        if categoria == "Table":
            _, numero = extrair_categoria_e_numero(nome)
            return numero
        elif categoria == "Dock" or categoria == "Divisoria":
            continue  # Ignora e espera novo clique
        else:
            obstáculo(win, x, y)  # Só aqui desenhas a mancha


def obstáculo(win, x, y):

    centro_imagem = Point(x, y)
    stain = Image(centro_imagem, "stain.gif")
    stain.draw(win)

class Waiter:
    def __init__(self, win, start_pos):
        self.win = win
        self.pos = Point(*start_pos)
        self.start_pos = Point(*start_pos)
        self.shape = Circle(self.pos, 4)
        self.shape.setFill("red")
        self.shape.draw(win)

    def move_to(self, destino):
        raio = 4  # raio do Waiter
        dx_total = destino.getX() - self.pos.getX()
        dy_total = destino.getY() - self.pos.getY()
        distancia = (dx_total**2 + dy_total**2) ** 0.5

        # Se já está suficientemente perto, não faz nada
        if distancia <= raio:
            return

        # Calcula o ponto final ajustado pelo raio
        fator = (distancia - raio) / distancia
        destino_x = self.pos.getX() + dx_total * fator
        destino_y = self.pos.getY() + dy_total * fator

        dx = (destino_x - self.pos.getX()) / 100
        dy = (destino_y - self.pos.getY()) / 100

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

def bfs(start, goal, obstacles, largura, altura):
    """Procura caminho do start ao goal evitando obstáculos usando BFS."""
    queue = deque()
    queue.append((start, [start]))
    visited = set()
    visited.add(start)

    # Movimentos possíveis: cima, baixo, esquerda, direita
    moves = [(-1,0), (1,0), (0,-1), (0,1)]

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return path

        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < largura and 0 <= ny < altura and (nx, ny) not in visited and (nx, ny) not in obstacles:
                queue.append(((nx, ny), path + [(nx, ny)]))
                visited.add((nx, ny))
    return None  # Sem caminho

def main():
    largura_logica = 150
    altura_logica = 150

    win = GraphWin("Sala do Restaurante", 600, 600)
    win.setCoords(0, 0, largura_logica, altura_logica)

    objetos = ler_ficheiro_planta("salaxx.txt")
    desenhar_objetos(objetos, win)
    
    empregado = Waiter(win, (68.5, 145))

    # Extrai as células ocupadas por divisórias (move este bloco para aqui!)
    obstacles = set()
    for obj in objetos:
        if obj['categoria'] in ("Divisoria", "Table", "Dock"):
            x1, y1 = obj['p1']
            x2, y2 = obj['p2']
            for x in range(min(x1, x2), max(x1, x2)+1):
                for y in range(min(y1, y2), max(y1, y2)+1):
                    obstacles.add((x, y))

    mesa_numero = receive_click(win, objetos)

    mesa_obj = None
    for obj in objetos:
        if obj['categoria'] == "Table":
            _, numero = extrair_categoria_e_numero(obj['nome'])
            if numero == mesa_numero:
                mesa_obj = obj
                continue

    if mesa_obj:
        # Calcula o centro da mesa
        mesa_x = (mesa_obj['p1'][0] + mesa_obj['p2'][0]) / 2
        mesa_y = (mesa_obj['p1'][1] + mesa_obj['p2'][1]) / 2

        # Posição atual do empregado
        emp_x = empregado.pos.getX()
        emp_y = empregado.pos.getY()

        # Vetor direção do empregado para a mesa
        dx = mesa_x - emp_x
        dy = mesa_y - emp_y
        dist = (dx**2 + dy**2) ** 0.5

        raio = 4  # raio do Waiter
        if dist > raio:
            # Ajusta o destino para parar a "raio" da mesa
            fator = (dist - raio) / dist
            destino_x = emp_x + dx * fator
            destino_y = emp_y + dy * fator
        else:
            destino_x = emp_x
            destino_y = emp_y

        destino = Point(destino_x, destino_y)
        empregado.move_to(destino)

        start = (int(empregado.pos.getX()), int(empregado.pos.getY()))
        goal = (int(mesa_x), int(mesa_y))
        path = bfs(start, goal, obstacles, largura_logica, altura_logica)

        if path:
            for px, py in path[1:]:
                empregado.shape.move(px - empregado.pos.getX(), py - empregado.pos.getY())
                empregado.pos.move(px - empregado.pos.getX(), py - empregado.pos.getY())
                sleep(0.01)
        else:
            print("Não existe caminho possível!")

        sleep(2)
        empregado.voltar()
        win.getMouse()
        win.close()

if __name__ == "__main__":
    main()
