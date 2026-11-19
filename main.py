import pygame
import pgzrun
import random
import math

WIDTH = 800
HEIGHT = 600
TITLE = "Meu primeiro jogo em Pygame"

VIDAS = 3
pontos = 0
PONTOS_VITORIA = 10
estado_jogo = "JOGANDO"

tempo_invulneravel = 0
TEMPO_INVULNERAVEL = 1.5

paredes = [
    Rect(220, 120, 30, 220),
    Rect(540, 260, 30, 220),
    Rect(300, 440, 200, 30),
]

heroi = Actor("gato_64x64")
heroi.pos = (400, 300)

Moeda = Actor("moeda_64x64")

inimigo = Actor("gato_64x64")
inimigo.pos = (100, 100)

Rota = [
    (100, 100),
    (100, 520),
    (700, 520),
    (700, 100),
]

ponto_rota = 0
estado_inimigo = "PATRULHANDO"

tempo_sem_ver = 0
TEMPO_INVESTIGACAO = 3.0

RAIO_VISAO = 180

ultima_posicao_heroi = None


def distancia(a, b):
    return math.sqrt(
        (a.x - b.x) ** 2 +
        (a.y - b.y) ** 2
    )


def hitbox_ator(ator):
    return Rect(ator.x - 20, ator.y - 20, 40, 40)


def colide_parede(ator):
    caixa = hitbox_ator(ator)
    return caixa.collidelist(paredes) != -1


def posicionar_sem_colisao(ator):
    while True:
        ator.pos = (
            random.randint(60, WIDTH - 60),
            random.randint(60, HEIGHT - 60)
        )
        if not colide_parede(ator) and distancia(ator, heroi) > 100:
            break


def mover_com_colisao(ator, dx, dy):
    bateu_x = False
    bateu_y = False

    ator.x += dx
    caixa = hitbox_ator(ator)
    for parede in paredes:
        if caixa.colliderect(parede):
            bateu_x = True
            if dx > 0:
                ator.x = parede.left - 20
            elif dx < 0:
                ator.x = parede.right + 20

    ator.y += dy
    caixa = hitbox_ator(ator)
    for parede in paredes:
        if caixa.colliderect(parede):
            bateu_y = True
            if dy > 0:
                ator.y = parede.top - 20
            elif dy < 0:
                ator.y = parede.bottom + 20

    return bateu_x, bateu_y


def mover_inimigo_inteligente(destino_x, destino_y, velocidade):
    dx = destino_x - inimigo.x
    dy = destino_y - inimigo.y
    dist = math.sqrt(dx ** 2 + dy ** 2)

    if dist > 0:
        vx = (dx / dist) * velocidade
        vy = (dy / dist) * velocidade

        bateu_x, bateu_y = mover_com_colisao(inimigo, vx, vy)

        if bateu_x and abs(vy) < 0.5:
            direcao_y = 1 if destino_y >= inimigo.y else -1
            mover_com_colisao(inimigo, 0, direcao_y * velocidade)

        if bateu_y and abs(vx) < 0.5:
            direcao_x = 1 if destino_x >= inimigo.x else -1
            mover_com_colisao(inimigo, direcao_x * velocidade, 0)

    inimigo.x = max(32, min(WIDTH - 32, inimigo.x))
    inimigo.y = max(32, min(HEIGHT - 32, inimigo.y))


posicionar_sem_colisao(Moeda)


def heroi_na_visao():
    dist = distancia(inimigo, heroi)
    return dist <= RAIO_VISAO


def patrulhar():
    global ponto_rota

    velocidade = 2
    destino = Rota[ponto_rota]

    dx = destino[0] - inimigo.x
    dy = destino[1] - inimigo.y
    distancia_total = math.sqrt(dx ** 2 + dy ** 2)

    mover_inimigo_inteligente(destino[0], destino[1], velocidade)

    if distancia_total < 15:
        ponto_rota += 1
        if ponto_rota >= len(Rota):
            ponto_rota = 0


def perseguir():
    mover_inimigo_inteligente(heroi.x, heroi.y, 2.5)


def reiniciar_jogo():
    global pontos, VIDAS, estado_jogo, tempo_invulneravel, estado_inimigo, ponto_rota
    pontos = 0
    VIDAS = 3
    estado_jogo = "JOGANDO"
    tempo_invulneravel = 0
    estado_inimigo = "PATRULHANDO"
    ponto_rota = 0
    heroi.pos = (400, 300)
    inimigo.pos = (100, 100)
    posicionar_sem_colisao(Moeda)


def draw():
    screen.fill((0, 20, 255))

    if estado_jogo == "JOGANDO":
        if estado_inimigo == "PERSEGUINDO":
            cor_visao = (255, 50, 50)
        else:
            cor_visao = (100, 100, 255)

        screen.draw.circle(inimigo.pos, RAIO_VISAO, cor_visao)

        for parede in paredes:
            screen.draw.filled_rect(parede, (80, 80, 90))
            screen.draw.rect(parede, "white")

        heroi.draw()
        inimigo.draw()
        Moeda.draw()

        screen.draw.text(
            f"Pontos: {pontos}/{PONTOS_VITORIA}",
            topleft=(20, 20),
            fontsize=32,
            color="purple",
            shadow=(1, 1),
            scolor="black"
        )

        screen.draw.text(
            f"Vidas: {VIDAS}",
            topleft=(20, 60),
            fontsize=32,
            color="red",
            shadow=(1, 1),
            scolor="black"
        )

    elif estado_jogo == "GAMEOVER":
        screen.draw.text(
            "GAME OVER",
            center=(WIDTH // 2, 250),
            fontsize=64,
            color="red",
            shadow=(2, 2),
            scolor="black"
        )

        screen.draw.text(
            f"Pontos: {pontos}",
            center=(WIDTH // 2, 330),
            fontsize=36,
            color="white"
        )

        screen.draw.text(
            "Pressione 'R' para reiniciar",
            center=(WIDTH // 2, 400),
            fontsize=24,
            color="white"
        )

    elif estado_jogo == "VITORIA":
        screen.draw.text(
            "VOCÊ VENCEU!",
            center=(WIDTH // 2, 250),
            fontsize=64,
            color="yellow",
            shadow=(2, 2),
            scolor="black"
        )

        screen.draw.text(
            f"Pontos: {pontos}",
            center=(WIDTH // 2, 330),
            fontsize=36,
            color="white"
        )

        screen.draw.text(
            "Pressione 'R' para reiniciar",
            center=(WIDTH // 2, 400),
            fontsize=24,
            color="white"
        )

    if estado_jogo == "JOGANDO":
        if estado_inimigo == "PERSEGUINDO":
            status_alerta = "ALERTA: INIMIGO TE VIU!"
        else:
            status_alerta = "Status: Oculto"

        screen.draw.text(
            status_alerta,
            midbottom=(WIDTH // 2, HEIGHT - 15),
            fontsize=22,
            color="crimson" if estado_inimigo == "PERSEGUINDO" else "lime"
        )


def update(dt):
    global pontos
    global VIDAS
    global estado_jogo
    global estado_inimigo
    global tempo_sem_ver
    global ultima_posicao_heroi
    global tempo_invulneravel

    if estado_jogo in ["VITORIA", "GAMEOVER"]:
        if keyboard.r:
            reiniciar_jogo()
        return

    if tempo_invulneravel > 0:
        tempo_invulneravel -= dt

    dx = 0
    dy = 0
    if keyboard.right:
        dx += 3
    if keyboard.left:
        dx -= 3
    if keyboard.up:
        dy -= 3
    if keyboard.down:
        dy += 3

    mover_com_colisao(heroi, dx, dy)

    heroi.x = max(32, min(WIDTH - 32, heroi.x))
    heroi.y = max(32, min(HEIGHT - 32, heroi.y))

    viu_heroi = heroi_na_visao()

    if viu_heroi:
        estado_inimigo = "PERSEGUINDO"
        ultima_posicao_heroi = (heroi.x, heroi.y)
        tempo_sem_ver = 0
        perseguir()
    else:
        if estado_inimigo == "PERSEGUINDO":
            tempo_sem_ver += dt

            if ultima_posicao_heroi is not None:
                dx = ultima_posicao_heroi[0] - inimigo.x
                dy = ultima_posicao_heroi[1] - inimigo.y
                dist = math.sqrt(dx ** 2 + dy ** 2)

                if dist > 10:
                    mover_inimigo_inteligente(
                        ultima_posicao_heroi[0],
                        ultima_posicao_heroi[1],
                        2
                    )

            if tempo_sem_ver >= TEMPO_INVESTIGACAO:
                estado_inimigo = "PATRULHANDO"
                tempo_sem_ver = 0
        else:
            estado_inimigo = "PATRULHANDO"
            patrulhar()

    if distancia(heroi, Moeda) < 38:
        pontos += 1
        posicionar_sem_colisao(Moeda)

    if distancia(inimigo, heroi) < 42 and tempo_invulneravel <= 0:
        VIDAS -= 1
        pontos = max(0, pontos - 1)
        tempo_invulneravel = TEMPO_INVULNERAVEL
        posicionar_sem_colisao(heroi)

        if VIDAS <= 0:
            estado_jogo = "GAMEOVER"

    if pontos >= PONTOS_VITORIA:
        estado_jogo = "VITORIA"


pgzrun.go()