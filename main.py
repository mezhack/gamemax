import os
import sys
import math
import random
from collections import deque
from pathlib import Path

import pygame

# Inicialização
pygame.init()

# O labirinto ocupa 720x720. O restante da janela fica livre para a interface.
LARGURA_MAZE, ALTURA_MAZE = 720, 720
LARGURA, ALTURA = 800, 720
OFFSET_X = (LARGURA - LARGURA_MAZE) // 2
OFFSET_Y = 0
CELL_SIZE = 16
COLS = LARGURA_MAZE // CELL_SIZE
ROWS = ALTURA_MAZE // CELL_SIZE

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Operação Stealth - Labirinto")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("arial", 21, bold=True)
fonte_menor = pygame.font.SysFont("arial", 16, bold=True)

# Cores
PRETO = (20, 20, 25)
VERDE_HEROI = (50, 220, 100)
VERMELHO_GUARDA = (230, 50, 50)
ROXO_GUARDA = (190, 70, 230)
AMARELO_CHAVE = (255, 215, 0)
AZUL_PORTA = (50, 130, 240)
BRANCO = (255, 255, 255)

# O labirinto deve ficar ao lado do arquivo .py. Também aceitamos o diretório
# atual para facilitar a execução em IDEs e ambientes escolares.
PASTA_DO_PROGRAMA = Path(__file__).resolve().parent
CAMINHOS_LABIRINTO = (
    PASTA_DO_PROGRAMA / "labirinto.png",
    Path.cwd() / "labirinto.png",
)
CAMINHO_LABIRINTO = next(
    (caminho for caminho in CAMINHOS_LABIRINTO if caminho.exists()), None
)

if CAMINHO_LABIRINTO is None:
    raise FileNotFoundError(
        "Não encontrei 'labirinto.png'. Coloque esse arquivo na mesma pasta "
        f"do programa: {PASTA_DO_PROGRAMA}"
    )

labirinto_img = pygame.image.load(str(CAMINHO_LABIRINTO)).convert()
labirinto_img = pygame.transform.scale(labirinto_img, (LARGURA_MAZE, ALTURA_MAZE))


def ponto_e_parede(x, y):
    """Retorna True quando o ponto está sobre uma parede escura do PNG."""
    ix = int(x - OFFSET_X)
    iy = int(y - OFFSET_Y)

    if ix < 0 or iy < 0 or ix >= LARGURA_MAZE or iy >= ALTURA_MAZE:
        return True

    r, g, b = labirinto_img.get_at((ix, iy))[:3]
    brilho = (r + g + b) / 3
    return brilho < 150


def retangulo_colide_com_labirinto(retangulo):
    """Testa centro, cantos e pontos médios do personagem contra o PNG."""
    pontos = [
        (retangulo.centerx, retangulo.centery),
        (retangulo.left, retangulo.top),
        (retangulo.right - 1, retangulo.top),
        (retangulo.left, retangulo.bottom - 1),
        (retangulo.right - 1, retangulo.bottom - 1),
        (retangulo.centerx, retangulo.top),
        (retangulo.centerx, retangulo.bottom - 1),
        (retangulo.left, retangulo.centery),
        (retangulo.right - 1, retangulo.centery),
    ]
    return any(ponto_e_parede(x, y) for x, y in pontos)


def mover_com_colisao(retangulo, dx, dy):
    """Move separadamente nos eixos, permitindo deslizar nos corredores."""
    distancia = math.hypot(dx, dy)
    passos = max(1, int(distancia / 2) + 1)
    passo_x = dx / passos
    passo_y = dy / passos

    for _ in range(passos):
        retangulo.x += round(passo_x)
        if retangulo_colide_com_labirinto(retangulo):
            retangulo.x -= round(passo_x)

        retangulo.y += round(passo_y)
        if retangulo_colide_com_labirinto(retangulo):
            retangulo.y -= round(passo_y)


def celula_para_pos(coluna, linha):
    return (
        OFFSET_X + coluna * CELL_SIZE + CELL_SIZE // 2,
        OFFSET_Y + linha * CELL_SIZE + CELL_SIZE // 2,
    )


def pos_para_celula(x, y):
    coluna = int((x - OFFSET_X) // CELL_SIZE)
    linha = int((y - OFFSET_Y) // CELL_SIZE)
    return (
        max(0, min(COLS - 1, coluna)),
        max(0, min(ROWS - 1, linha)),
    )


def celula_livre(coluna, linha):
    x, y = celula_para_pos(coluna, linha)
    return not ponto_e_parede(x, y)


def construir_grafo():
    """Monta os corredores que serão usados pela busca de caminho."""
    livres = {
        (coluna, linha): celula_livre(coluna, linha)
        for linha in range(ROWS)
        for coluna in range(COLS)
    }
    grafo = {}
    for linha in range(ROWS):
        for coluna in range(COLS):
            origem = (coluna, linha)
            if not livres[origem]:
                continue
            vizinhos = []
            for dc, dl in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                destino = (coluna + dc, linha + dl)
                if not (0 <= destino[0] < COLS and 0 <= destino[1] < ROWS):
                    continue
                if not livres[destino]:
                    continue
                x1, y1 = celula_para_pos(*origem)
                x2, y2 = celula_para_pos(*destino)
                if not ponto_e_parede((x1 + x2) / 2, (y1 + y2) / 2):
                    vizinhos.append(destino)
            grafo[origem] = vizinhos
    return grafo


def bfs_caminho(grafo, origem, destino):
    """Retorna o menor caminho entre duas células livres do labirinto."""
    if origem not in grafo or destino not in grafo:
        return []
    if origem == destino:
        return []

    fila = deque([origem])
    anterior = {origem: None}
    while fila:
        atual = fila.popleft()
        if atual == destino:
            break
        for vizinho in grafo[atual]:
            if vizinho not in anterior:
                anterior[vizinho] = atual
                fila.append(vizinho)

    if destino not in anterior:
        return []

    caminho = []
    atual = destino
    while atual != origem:
        caminho.append(atual)
        atual = anterior[atual]
    caminho.reverse()
    return caminho


def tem_linha_de_visao(x1, y1, x2, y2):
    """O inimigo só enxerga o herói se não houver parede entre eles."""
    distancia = math.hypot(x2 - x1, y2 - y1)
    passos = max(1, int(distancia / 4))
    for i in range(1, passos):
        fator = i / passos
        if ponto_e_parede(x1 + (x2 - x1) * fator, y1 + (y2 - y1) * fator):
            return False
    return True


GRAFO_LABIRINTO = construir_grafo()
CELULAS_LIVRES = list(GRAFO_LABIRINTO.keys())


def posicao_livre_aleatoria(pos_evitar=None, distancia_minima=0):
    for _ in range(3000):
        celula = random.choice(CELULAS_LIVRES)
        x, y = celula_para_pos(*celula)
        if pos_evitar and math.hypot(x - pos_evitar[0], y - pos_evitar[1]) < distancia_minima:
            continue
        return x, y
    return celula_para_pos(*CELULAS_LIVRES[0])


class Inimigo:
    """Guarda com patrulha própria e perseguição pelo labirinto."""

    def __init__(self, cor, posicao_inicial, nome):
        self.cor = cor
        self.nome = nome
        # Os corredores têm cerca de 16 px; um corpo menor evita ficar preso
        # nas quinas das paredes do desenho.
        self.rect = pygame.Rect(0, 0, 10, 10)
        self.rect.center = posicao_inicial
        self.velocidade_patrulha = 42
        self.velocidade_perseguicao = 68
        self.estado = "PATRULHA"
        self.caminho = []
        self.destino_patrulha = None
        self.ultima_celula_jogador = None
        self.tempo_sem_perceber = 0
        self.tempo_recalculo = 0

    def percebe_jogador(self, jogador):
        distancia = math.hypot(
            jogador.centerx - self.rect.centerx,
            jogador.centery - self.rect.centery,
        )
        # A distância limita a visão, e as paredes podem bloqueá-la.
        return distancia <= 330 and tem_linha_de_visao(
            self.rect.centerx, self.rect.centery,
            jogador.centerx, jogador.centery,
        )

    def escolher_patrulha(self):
        self.destino_patrulha = random.choice(CELULAS_LIVRES)
        self.caminho = bfs_caminho(
            GRAFO_LABIRINTO,
            pos_para_celula(*self.rect.center),
            self.destino_patrulha,
        )

    def atualizar(self, jogador, dt):
        percebeu = self.percebe_jogador(jogador)
        celula_atual = pos_para_celula(*self.rect.center)

        if percebeu:
            self.estado = "PERSEGUINDO"
            self.tempo_sem_perceber = 0
            self.ultima_celula_jogador = pos_para_celula(*jogador.center)
        elif self.estado == "PERSEGUINDO":
            self.tempo_sem_perceber += dt
            if self.tempo_sem_perceber > 4:
                self.estado = "PATRULHA"
                self.caminho = []

        if self.estado == "PERSEGUINDO":
            self.tempo_recalculo -= dt
            if self.tempo_recalculo <= 0:
                self.tempo_recalculo = 0.2
                self.caminho = bfs_caminho(
                    GRAFO_LABIRINTO,
                    celula_atual,
                    self.ultima_celula_jogador,
                )
            velocidade = self.velocidade_perseguicao
        else:
            if not self.caminho:
                self.escolher_patrulha()
            velocidade = self.velocidade_patrulha

        self.mover_pelo_caminho(dt, velocidade)

    def mover_pelo_caminho(self, dt, velocidade):
        if not self.caminho:
            return
        alvo_x, alvo_y = celula_para_pos(*self.caminho[0])
        dx = alvo_x - self.rect.centerx
        dy = alvo_y - self.rect.centery
        distancia = math.hypot(dx, dy)
        if distancia < 3:
            self.caminho.pop(0)
            return

        posicao_anterior = self.rect.center
        mover_com_colisao(
            self.rect,
            (dx / distancia) * velocidade * dt,
            (dy / distancia) * velocidade * dt,
        )

        # Se uma quina bloquear o caminho, abandona a rota atual. No próximo
        # ciclo a patrulha ou a perseguição calcula outro caminho.
        if self.rect.center == posicao_anterior:
            self.caminho = []

    def desenhar(self):
        pygame.draw.rect(tela, self.cor, self.rect)
        if self.estado == "PERSEGUINDO":
            alerta = fonte_menor.render("!", True, (255, 80, 80))
            tela.blit(alerta, (self.rect.centerx - 4, self.rect.top - 17))


# Entidades e estados preservados do primeiro código.
heroi = pygame.Rect(0, 0, 10, 10)
chave = pygame.Rect(0, 0, 12, 12)
porta = pygame.Rect(0, 0, 18, 18)
guarda = Inimigo(VERMELHO_GUARDA, (0, 0), "G1")
guarda_2 = Inimigo(ROXO_GUARDA, (0, 0), "G2")
pegou_chave = False
status_jogo = "JOGANDO"


def reiniciar_jogo():
    global pegou_chave, status_jogo
    inicio = posicao_livre_aleatoria()
    heroi.center = inicio
    g1 = posicao_livre_aleatoria(inicio, 180)
    g2 = posicao_livre_aleatoria(inicio, 180)
    guarda.rect.center = g1
    guarda_2.rect.center = g2
    chave.center = posicao_livre_aleatoria(inicio, 100)
    porta.center = posicao_livre_aleatoria(chave.center, 180)
    for inimigo in (guarda, guarda_2):
        inimigo.estado = "PATRULHA"
        inimigo.caminho = []
        inimigo.tempo_sem_perceber = 0
    pegou_chave = False
    status_jogo = "JOGANDO"


reiniciar_jogo()

while True:
    dt = relogio.tick(60) / 1000.0
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            reiniciar_jogo()

    if status_jogo == "JOGANDO":
        teclas = pygame.key.get_pressed()
        dx = int(teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) - int(
            teclas[pygame.K_LEFT] or teclas[pygame.K_a]
        )
        dy = int(teclas[pygame.K_DOWN] or teclas[pygame.K_s]) - int(
            teclas[pygame.K_UP] or teclas[pygame.K_w]
        )
        if dx or dy:
            tamanho = math.hypot(dx, dy)
            mover_com_colisao(heroi, (dx / tamanho) * 130 * dt, (dy / tamanho) * 130 * dt)

        if not pegou_chave and heroi.colliderect(chave):
            pegou_chave = True

        # Os dois usam a mesma lógica de perseguição, mas com estado/caminho próprios.
        guarda.atualizar(heroi, dt)
        guarda_2.atualizar(heroi, dt)

        if heroi.colliderect(guarda.rect) or heroi.colliderect(guarda_2.rect):
            status_jogo = "PERDEU"
        elif pegou_chave and heroi.colliderect(porta):
            status_jogo = "VENCEU"

    # Renderização
    tela.fill(PRETO)
    tela.blit(labirinto_img, (OFFSET_X, OFFSET_Y))

    pygame.draw.rect(tela, AZUL_PORTA, porta)
    if not pegou_chave:
        pygame.draw.rect(tela, AMARELO_CHAVE, chave)

    pygame.draw.rect(tela, VERDE_HEROI, heroi)
    guarda.desenhar()
    guarda_2.desenhar()

    texto_chave = "Chave: OK!" if pegou_chave else "Chave: Pendente"
    hud = fonte.render(texto_chave, True, BRANCO)
    tela.blit(hud, (8, 8))
    ajuda = fonte_menor.render("WASD/setas: mover  |  R: reiniciar", True, BRANCO)
    tela.blit(ajuda, (8, ALTURA - 24))

    if status_jogo == "PERDEU":
        msg = fonte.render("CAPTURADO! Pressione R para tentar novamente.", True, VERMELHO_GUARDA)
        tela.blit(msg, (120, ALTURA // 2))
    elif status_jogo == "VENCEU":
        msg = fonte.render("ESCAPOU COM SUCESSO! Pressione R para jogar.", True, VERDE_HEROI)
        tela.blit(msg, (120, ALTURA // 2))

    pygame.display.flip()
