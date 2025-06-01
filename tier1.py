#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 22 18:23:31 2025

@author: stelafernandes
"""

from graphics import GraphWin, Rectangle, Oval, Point
from waiter import Waiter

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
            # Extrair tipo: antes do primeiro '(' na segunda parte
            tipo = partes[1].split('(')[0]

            # Extrair a parte que contém os pontos (juntando partes[1:] para garantir)
            pontos_str = ' '.join(partes[1:])
            # Agora pontos_str é algo como: "Rectangle(Point(0,0), Point(80,60))"
            
            # Encontrar os dois Point(...)
            import re
            pontos = re.findall(r'Point\((\d+),(\d+)\)', pontos_str)
            if len(pontos) != 2:
                print(f"Linha ignorada por não ter exatamente 2 pontos: {linha}")
                continue
            
            p1x, p1y = map(int, pontos[0])
            p2x, p2y = map(int, pontos[1])

            objeto = {
                'nome': nome,
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

def main():
    largura_logica = 150
    altura_logica = 150

    win = GraphWin("Sala do Restaurante", 600, 600)
    win.setCoords(0, 0, largura_logica, altura_logica)

    objetos = ler_ficheiro_planta("salaxx.txt")
    desenhar_objetos(objetos, win)

    waiter = Waiter(win, (93, 145))  # Posição inicial do garçom

    destino = Point(50, 50)  # Posição de destino do garçom
    waiter.move_to(destino)  # Move o garçom para a posição de destino
    waiter.voltar()  # Move o garçom de volta para a posição inicial

    # Espera por um clique para fechar
    win.getMouse()
    win.close()

main()
