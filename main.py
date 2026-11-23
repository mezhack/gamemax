
import pygame
import random
import sys
from collections import deque

pygame.init()

# CONFIGURACOES
LARGURA, ALTURA = 800, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Operacao Stealth - Pacman Edition")

RELOGIO = pygame.time.Clock()
FONTE = pygame.font.SysFont("arial", 20, bold=True)
GRANDE = pygame.font.SysFont("arial", 36, bold=True)

TAMANHO = 36
COLUNAS, LINHAS = 21, 15
OX, OY = 22, 48

FUNDO = (15, 15, 23)
CHAO = (28, 28, 39)
PAREDE = (75, 75, 105)
VERDE = (40, 230, 110)
VERMELHO = (240, 45, 55)
LARANJA = (255, 145, 30)
AZUL = (40, 160, 255)
ROXO = (180, 60, 255)
AMARELO = (255, 220, 0)
BRANCO = (255, 255, 255)

TOTAL_PONTOS = 12

# GERAR LABIRINTO
def gerar_labirinto():
    mapa = [["#" for _ in range(COLUNAS)] for _ in range(LINHAS)]
    mapa[1][1] = "."
    pilha = [(1, 1)]

    while pilha:
        x, y = pilha[-1]
        opcoes = []

        for dx, dy in [(0,-2), (0,2), (-2,0), (2,0)]:
            nx, ny = x+dx, y+dy

            if 1 <= nx < COLUNAS-1 and 1 <= ny < LINHAS-1:
                if mapa[ny][nx] == "#":
                    opcoes.append((nx, ny))

        if opcoes:
            nx, ny = random.choice(opcoes)
            mapa[(y+ny)//2][(x+nx)//2] = "."
            mapa[ny][nx] = "."
            pilha.append((nx, ny))
        else:
            pilha.pop()

    paredes = []

    for y in range(1, LINHAS-1):
        for x in range(1, COLUNAS-1):
            if mapa[y][x] == "#":
                if ((mapa[y][x-1] == "." and mapa[y][x+1] == ".")
                    or (mapa[y-1][x] == "." and mapa[y+1][x] == ".")):
                    paredes.append((x, y))

    random.shuffle(paredes)

    for x, y in paredes[:24]:
        mapa[y][x] = "."

    return mapa


labirinto = gerar_labirinto()

# PAREDES
obstaculos = []

for y in range(LINHAS):
    for x in range(COLUNAS):
        if labirinto[y][x] == "#":
            obstaculos.append(pygame.Rect(
                OX+x*TAMANHO, OY+y*TAMANHO,
                TAMANHO, TAMANHO
            ))


# POSICOES
def centro(x, y):
    return (
        OX+x*TAMANHO+TAMANHO//2,
        OY+y*TAMANHO+TAMANHO//2
    )


def criar_personagem(x, y):
    cx, cy = centro(x, y)
    return pygame.Rect(cx-11, cy-11, 22, 22)


def obter_celula(p):
    return (
        int((p.centerx-OX)//TAMANHO),
        int((p.centery-OY)//TAMANHO)
    )


def vizinhos(x, y):
    resultado = []

    for dx, dy in [(0,-1), (0,1), (-1,0), (1,0)]:
        nx, ny = x+dx, y+dy

        if 0 <= nx < COLUNAS and 0 <= ny < LINHAS:
            if labirinto[ny][nx] == ".":
                resultado.append((nx, ny))

    return resultado


# CAMINHO MAIS CURTO
def encontrar_caminho(inicio, destino):
    fila = deque([inicio])
    anteriores = {inicio: None}

    while fila:
        atual = fila.popleft()

        if atual == destino:
            break

        for v in vizinhos(*atual):
            if v not in anteriores:
                anteriores[v] = atual
                fila.append(v)

    if destino not in anteriores:
        return []

    caminho = []
    atual = destino

    while atual is not None:
        caminho.append(atual)
        atual = anteriores[atual]

    return caminho[::-1]


# MOVIMENTACAO
def mover(p, dx, dy):
    p.x += dx

    for parede in obstaculos:
        if p.colliderect(parede):
            if dx > 0:
                p.right = parede.left
            elif dx < 0:
                p.left = parede.right

    p.y += dy

    for parede in obstaculos:
        if p.colliderect(parede):
            if dy > 0:
                p.bottom = parede.top
            elif dy < 0:
                p.top = parede.bottom


def seguir_ponto(p, destino, velocidade):
    tx, ty = centro(*destino)
    dx = tx-p.centerx
    dy = ty-p.centery

    if dx != 0:
        mover(p, max(-velocidade, min(velocidade, dx)), 0)
    elif dy != 0:
        mover(p, 0, max(-velocidade, min(velocidade, dy)))


def chegou(p, destino):
    cx, cy = centro(*destino)
    return abs(p.centerx-cx) <= 2 and abs(p.centery-cy) <= 2


# PATRULHA INTELIGENTE
def patrulhar(p, estado):
    atual = obter_celula(p)
    destino = estado["destino"]

    if destino is None or chegou(p, destino):
        estado["anterior"] = estado["atual"]
        estado["atual"] = atual

        opcoes = [
            v for v in vizinhos(*atual)
            if v != estado["anterior"]
        ]

        if not opcoes:
            opcoes = vizinhos(*atual)

        estado["destino"] = (
            random.choice(opcoes) if opcoes else atual
        )

    seguir_ponto(p, estado["destino"], estado["velocidade"])


# REINICIAR
def reiniciar():
    global heroi, inimigos, chave, porta
    global pontos, pegou_chave, status, contador

    heroi = criar_personagem(1, 1)
    chave = criar_personagem(19, 13)
    porta = criar_personagem(1, 13)

    # Quatro inimigos
    inimigos = [
        {
            "nome": "vermelho",
            "cor": VERMELHO,
            "pos": criar_personagem(19, 1),
            "tipo": "perseguidor",
            "velocidade": 3,
            "contador": 0,
            "intervalo": 3
        },
        {
            "nome": "laranja",
            "cor": LARANJA,
            "pos": criar_personagem(11, 7),
            "tipo": "patrulha",
            "velocidade": 2,
            "destino": None,
            "anterior": None,
            "atual": (11, 7)
        },
        {
            "nome": "azul",
            "cor": AZUL,
            "pos": criar_personagem(1, 7),
            "tipo": "patrulha",
            "velocidade": 2,
            "destino": None,
            "anterior": None,
            "atual": (1, 7)
        },
        {
            "nome": "roxo",
            "cor": ROXO,
            "pos": criar_personagem(19, 7),
            "tipo": "perseguidor",
            "velocidade": 2,
            "contador": 0,
            "intervalo": 7
        }
    ]

    # Criar pontos em celulas livres
    ocupadas = {
        (1, 1), (19, 1), (11, 7),
        (1, 7), (19, 7), (19, 13), (1, 13)
    }

    livres = [
        (x, y)
        for y in range(1, LINHAS-1)
        for x in range(1, COLUNAS-1)
        if labirinto[y][x] == "."
        and (x, y) not in ocupadas
    ]

    escolhidos = random.sample(livres, TOTAL_PONTOS)

    pontos = [
        pygame.Rect(
            centro(x, y)[0]-5,
            centro(x, y)[1]-5,
            10, 10
        )
        for x, y in escolhidos
    ]

    pegou_chave = False
    status = "JOGANDO"
    contador = 0


reiniciar()

# LOOP PRINCIPAL
while True:
    RELOGIO.tick(60)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                reiniciar()

    if status == "JOGANDO":

        # JOGADOR
        teclas = pygame.key.get_pressed()

        dx = int(teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) - \
             int(teclas[pygame.K_LEFT] or teclas[pygame.K_a])

        dy = int(teclas[pygame.K_DOWN] or teclas[pygame.K_s]) - \
             int(teclas[pygame.K_UP] or teclas[pygame.K_w])

        if dx:
            mover(heroi, dx*3, 0)

        if dy:
            mover(heroi, 0, dy*3)

        # COLETAR PONTOS
        for ponto in pontos[:]:
            if heroi.colliderect(ponto):
                pontos.remove(ponto)

        # COLETAR CHAVE
        if heroi.colliderect(chave):
            pegou_chave = True

        # ABRIR PORTA
        if heroi.colliderect(porta):
            if pegou_chave and len(pontos) == 0:
                status = "VITORIA"

        # ATUALIZAR INIMIGOS
        for inimigo in inimigos:

            p = inimigo["pos"]

            if inimigo["tipo"] == "perseguidor":
                inimigo["contador"] += 1

                if inimigo["contador"] >= inimigo["intervalo"]:
                    inimigo["contador"] = 0

                    caminho = encontrar_caminho(
                        obter_celula(p),
                        obter_celula(heroi)
                    )

                    if len(caminho) > 1:
                        seguir_ponto(
                            p,
                            caminho[1],
                            inimigo["velocidade"]
                        )

            elif inimigo["tipo"] == "patrulha":
                patrulhar(p, inimigo)

            # COLISAO COM JOGADOR
            if heroi.colliderect(p):
                status = "DERROTA"

    # DESENHAR CENARIO
    TELA.fill(FUNDO)

    for y in range(LINHAS):
        for x in range(COLUNAS):
            cor = PAREDE if labirinto[y][x] == "#" else CHAO

            pygame.draw.rect(
                TELA, cor,
                (OX+x*TAMANHO, OY+y*TAMANHO,
                 TAMANHO-1, TAMANHO-1)
            )

    # DESENHAR PONTOS
    for ponto in pontos:
        pygame.draw.circle(
            TELA, AMARELO, ponto.center, 5
        )

    # CHAVE
    if not pegou_chave:
        pygame.draw.rect(TELA, AMARELO, chave, border_radius=5)

    # PORTA
    cor_porta = (
        VERDE if pegou_chave and len(pontos) == 0
        else VERMELHO
    )

    pygame.draw.rect(TELA, cor_porta, porta, border_radius=5)

    # PERSONAGEM
    pygame.draw.rect(
        TELA, (40, 130, 255), heroi, border_radius=6
    )

    # INIMIGOS
    for inimigo in inimigos:
        pygame.draw.rect(
            TELA, inimigo["cor"],
            inimigo["pos"], border_radius=6
        )

    # INFORMACOES
    TELA.blit(
        FONTE.render(
            f"PONTOS: {TOTAL_PONTOS-len(pontos)}/{TOTAL_PONTOS}",
            True, BRANCO
        ),
        (22, 10)
    )

    TELA.blit(
        FONTE.render(
            "CHAVE: " + ("SIM" if pegou_chave else "NAO"),
            True, AMARELO
        ),
        (260, 10)
    )

    # VITORIA E DERROTA
    if status != "JOGANDO":

        mensagem = (
            "VOCE VENCEU!"
            if status == "VITORIA"
            else "VOCE FOI CAPTURADO!"
        )

        cor = VERDE if status == "VITORIA" else VERMELHO

        texto = GRANDE.render(mensagem, True, cor)

        TELA.blit(
            texto,
            texto.get_rect(center=(LARGURA//2, ALTURA//2))
        )

        ajuda = FONTE.render(
            "Pressione R para jogar novamente",
            True, BRANCO
        )

        TELA.blit(
            ajuda,
            ajuda.get_rect(center=(LARGURA//2, ALTURA//2+45))
        )

    pygame.display.flip()