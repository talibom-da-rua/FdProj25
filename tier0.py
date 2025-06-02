#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 22 18:23:31 2025

@author: stelafernandes
"""

from graphics import GraphWin, Rectangle, Point

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
        
from graphics import Circle

class Waiter:
    def __init__(self, ponto_inicial, cor="blue", raio=20):
        self.ponto_inicial = ponto_inicial
        self.posicao_atual = ponto_inicial
        self.cor = cor
        self.raio = raio
        self.forma = None

    def desenhar(self, win):
        if self.forma:
            self.forma.undraw()
        self.forma = Circle(self.posicao_atual, self.raio)
        self.forma.setFill(self.cor)
        self.forma.setOutline("black")
        self.forma.draw(win)


def main():
    largura_logica = 150
    altura_logica = 150

    win = GraphWin("Sala do Restaurante", 600, 600)
    win.setCoords(0, 0, largura_logica, altura_logica)

    objetos = ler_ficheiro_planta("salaxx.txt")
    desenhar_objetos(objetos, win)
    
    # Criar e desenhar o empregado no ponto inicial
    ponto_inicial = Point(68.5, 145)  # centro do Dock1
    empregado = Waiter(ponto_inicial, raio=4)
    empregado.desenhar(win)


    # Espera por um clique para fechar
    receive_click(win, objetos)
    win.close()

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
            continue
        elif categoria is None:
            obstáculo(win, x, y)  # Só aqui desenhas a mancha


def obstáculo(win, x, y):

    centro_imagem = Point(x, y)
    stain = Image(centro_imagem, "stain.gif")
    stain.draw(win)

