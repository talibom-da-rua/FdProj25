from graphics import GraphWin, Rectangle, Oval, Point, Circle
from collections import deque
from time import sleep
import re

# ===============================
# Função: Ler os objetos da planta
# ===============================
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
            tipo = partes[1].split('(')[0]
            pontos_str = ' '.join(partes[1:])
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

# ===============================
# Função: Desenhar objetos na janela
# ===============================
def desenhar_objetos(objetos, win):
    for obj in objetos:
        p1 = Point(*obj['p1'])
        p2 = Point(*obj['p2'])
        if obj['tipo'] == "Rectangle":
            forma = Rectangle(p1, p2)
        elif obj['tipo'] == "Oval":
            forma = Oval(p1, p2)
        else:
            continue
        forma.setFill("lightgrey")
        forma.draw(win)

# ===============================
# Função: Obter os destinos (centros) das mesas
# ===============================
def obter_destinos_das_mesas(objetos):
    destinos = []
    for obj in objetos:
        if "table" in obj['nome'].lower():
            x1, y1 = obj['p1']
            x2, y2 = obj['p2']
            centro_x = (x1 + x2) / 2
            centro_y = (y1 + y2) / 2
            destino = Point(centro_x, max(y1, y2) + 2)  # ligeiramente acima
            destinos.append(destino)
    return destinos

# ===============================
# Função: Obter obstáculos como grelha
# ===============================
def obter_obstaculos_em_grelha(objetos):
    obstaculos = set()
    for obj in objetos:
        if obj['tipo'] == 'Rectangle' and ("table" in obj['nome'].lower() or "divisoria" in obj['nome'].lower()):
            x1, y1 = obj['p1']
            x2, y2 = obj['p2']
            for x in range(min(x1, x2), max(x1, x2)+1):
                for y in range(min(y1, y2), max(y1, y2)+1):
                    obstaculos.add((x, y))
    return obstaculos

# ===============================
# Função: Busca em Largura (BFS)
# ===============================
def bfs(start, goal, obstacles, largura, altura):
    queue = deque()
    queue.append((start, [start]))
    visited = set()
    visited.add(start)

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
    return None

# ===============================
# Classe: Waiter
# ===============================
class Waiter:
    def __init__(self, ponto_inicial, cor="blue", raio=4):
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

    def mover_com_bfs(self, destino, win, objetos, largura, altura):
        start = (int(round(self.posicao_atual.getX())), int(round(self.posicao_atual.getY())))
        end = (int(round(destino.getX())), int(round(destino.getY())))
        obstaculos = obter_obstaculos_em_grelha(objetos)

        caminho = bfs(start, end, obstaculos, largura, altura)
        if not caminho:
            print("Sem caminho para o destino!")
            return

        for px, py in caminho[1:]:
            proximo = Point(px, py)
            dx = proximo.getX() - self.posicao_atual.getX()
            dy = proximo.getY() - self.posicao_atual.getY()
            self.forma.move(dx, dy)
            self.posicao_atual = proximo
            sleep(0.01)
            win.update()

def verificar_clique_em_mesa(ponto, objetos):
    for obj in objetos:
        if "table" in obj['nome'].lower():
            x1, y1 = obj['p1']
            x2, y2 = obj['p2']
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)

            if min_x <= ponto.getX() <= max_x and min_y <= ponto.getY() <= max_y:
                centro_x = (x1 + x2) / 2
                centro_y = (y1 + y2) / 2
                destino = Point(centro_x, max(y1, y2) + 2)
                return destino, obj['nome']
    return None, None

# ===============================
# Função principal
# ===============================
def main():
    largura_logica = 150
    altura_logica = 150

    win = GraphWin("Sala do Restaurante", 600, 600)
    win.setCoords(0, 0, largura_logica, altura_logica)
    win.setBackground("white")

    objetos = ler_ficheiro_planta("salaxx.txt")
    desenhar_objetos(objetos, win)

    ponto_inicial = Point(68.5, 145)
    empregado = Waiter(ponto_inicial)
    empregado.desenhar(win)

    print("Clique numa mesa para fazer um pedido (ESC para sair).")

    while True:
        clique = win.checkMouse()
        if clique:
            destino, nome_mesa = verificar_clique_em_mesa(clique, objetos)
            if destino:
                print(f"Pedido recebido para: {nome_mesa}")
                empregado.mover_com_bfs(destino, win, objetos, largura_logica, altura_logica)
                sleep(2)  # tempo de entrega
                empregado.mover_com_bfs(empregado.ponto_inicial, win, objetos, largura_logica, altura_logica)
        sleep(0.05)

        # Check ESC key
        key = win.checkKey()
        if key.lower() == "escape":
            break

    win.close()


if __name__ == "__main__":
    main()
