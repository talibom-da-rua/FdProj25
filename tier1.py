from graphics import GraphWin, Rectangle, Oval, Point, Circle
from collections import deque

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
# Função: Obter os centros das mesas
# ===============================
def obter_centros_das_mesas(objetos):
    centros = []
    for obj in objetos:
        if "table" in obj['nome'].lower():  # <-- correção aqui
            x1, y1 = obj['p1']
            x2, y2 = obj['p2']
            centro_x = (x1 + x2) / 2
            centro_y = (y1 + y2) / 2
            centros.append(Point(centro_x, centro_y))
    return centros

# ===============================
# Função: Verificar colisão com obstáculos
# ===============================
def esta_em_colisao(ponto, objetos):
    x = ponto.getX()
    y = ponto.getY()
    for obj in objetos:
        if obj['tipo'] == 'Rectangle' and ("table" in obj['nome'].lower() or "divisiora" in obj['nome'].lower()):
            x1, y1 = obj['p1']
            x2, y2 = obj['p2']
            if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
                return True
    return False

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

    def mover_com_desvio(self, destino, win, objetos):
        passo = 2
        atual = self.posicao_atual

        while abs(atual.getX() - destino.getX()) >= passo or abs(atual.getY() - destino.getY()) >= passo:
            if abs(destino.getX() - atual.getX()) >= passo:
                inc_x = passo if destino.getX() > atual.getX() else -passo
                proximo = Point(atual.getX() + inc_x, atual.getY())
            elif abs(destino.getY() - atual.getY()) >= passo:
                inc_y = passo if destino.getY() > atual.getY() else -passo
                proximo = Point(atual.getX(), atual.getY() + inc_y)
            else:
                break

            if not esta_em_colisao(proximo, objetos):
                desloca_x = proximo.getX() - atual.getX()
                desloca_y = proximo.getY() - atual.getY()
                self.forma.move(desloca_x, desloca_y)
                self.posicao_atual = proximo
                atual = proximo
                win.update()
            else:
                # Tenta desviar no eixo contrário
                if abs(destino.getY() - atual.getY()) >= passo:
                    desvio = passo if destino.getY() > atual.getY() else -passo
                    tentativa = Point(atual.getX(), atual.getY() + desvio)
                else:
                    desvio = passo if destino.getX() > atual.getX() else -passo
                    tentativa = Point(atual.getX() + desvio, atual.getY())

                if not esta_em_colisao(tentativa, objetos):
                    desloca_x = tentativa.getX() - atual.getX()
                    desloca_y = tentativa.getY() - atual.getY()
                    self.forma.move(desloca_x, desloca_y)
                    self.posicao_atual = tentativa
                    atual = tentativa
                    win.update()
                else:
                    break  # preso

# ===============================
# Função: Busca em Largura (BFS)
# ===============================
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

# ===============================
# Função principal
# ===============================
def main():
    largura_logica = 150
    altura_logica = 150

    win = GraphWin("Sala do Restaurante", 600, 600)
    win.setCoords(0, 0, largura_logica, altura_logica)

    objetos = ler_ficheiro_planta("salaxx.txt")
    desenhar_objetos(objetos, win)

    centros = obter_centros_das_mesas(objetos)
    for centro in centros:
        circulo = Circle(centro, 1)
        circulo.setFill("red")
        circulo.draw(win)

    ponto_inicial = Point(68.5, 145)  # centro do Dock1
    empregado = Waiter(ponto_inicial)
    empregado.desenhar(win)

    for centro in centros:
        empregado.mover_com_desvio(centro, win, objetos)
        empregado.mover_com_desvio(empregado.ponto_inicial, win, objetos)
    win.getMouse()  # <-- Adiciona esta linha
    win.getMouse()  # <-- Adiciona esta linha
    win.close()     # <-- E esta

if __name__ == "__main__":
    main()
