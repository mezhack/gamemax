import pygame
import pgzrun
import random
import math

WIDTH = 800
HEIGHT = 600
TITLE = "Meu primeiro jogo em Pygame"

VIDA = 3
pontos = 0
PONTOS_VITORIA = 10
estado_jogo = "JOGANDO"

paredes = [
    Rect((180, 140), (30, 220)),
    Rect((580, 240), (30, 220)),
    Rect((300, 460), (200, 30))
]

heroi = Actor("imagem_64x64")
heroi.pos = (400, 300)

Moeda = Actor("moeda_64x64")

inimigo = Actor("cachorro_minion_64x64")
inimigo.pos = (
    random.randint(50, WIDTH - 50),
    random.randint(50, HEIGHT - 50)
)


def posicionar_moeda():
    while True:
        Moeda.pos = (
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50)
        )
        if not any(Moeda.colliderect(p) for p in paredes):
            break


posicionar_moeda()

estado_inimigo = "PATRULHANDO"
direcao_patrulha = "DIREITA"
tempo_sem_ver = 0
TEMPO_INVESTIGACAO = 3.0
RAIO_VISAO = 180
ultima_posicao_heroi = None
direcao_investigacao = 1


def distancia(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def heroi_na_visao():
    return distancia(inimigo, heroi) <= RAIO_VISAO


def colidiu_parede(ator):
    for parede in paredes:
        if ator.colliderect(parede):
            return True
    return False


def patrulhar():
    global direcao_patrulha
    velocidade = 2
    x_antigo, y_antigo = inimigo.x, inimigo.y

    if direcao_patrulha == "DIREITA":
        inimigo.x += velocidade
        if inimigo.x >= WIDTH - 50 or colidiu_parede(inimigo):
            inimigo.x = x_antigo
            direcao_patrulha = "BAIXO"

    elif direcao_patrulha == "BAIXO":
        inimigo.y += velocidade
        if inimigo.y >= HEIGHT - 50 or colidiu_parede(inimigo):
            inimigo.y = y_antigo
            direcao_patrulha = "ESQUERDA"

    elif direcao_patrulha == "ESQUERDA":
        inimigo.x -= velocidade
        if inimigo.x <= 50 or colidiu_parede(inimigo):
            inimigo.x = x_antigo
            direcao_patrulha = "CIMA"

    elif direcao_patrulha == "CIMA":
        inimigo.y -= velocidade
        if inimigo.y <= 50 or colidiu_parede(inimigo):
            inimigo.y = y_antigo
            direcao_patrulha = "DIREITA"


def perseguir():
    velocidade = 2.5
    dx = heroi.x - inimigo.x
    dy = heroi.y - inimigo.y
    distancia_total = math.sqrt(dx ** 2 + dy ** 2)

    if distancia_total > 0:
        x_antigo = inimigo.x
        inimigo.x += (dx / distancia_total) * velocidade
        if colidiu_parede(inimigo):
            inimigo.x = x_antigo

        y_antigo = inimigo.y
        inimigo.y += (dy / distancia_total) * velocidade
        if colidiu_parede(inimigo):
            inimigo.y = y_antigo


def investigar():
    global direcao_investigacao
    velocidade = 1.5
    x_antigo = inimigo.x

    inimigo.x += velocidade * direcao_investigacao

    if inimigo.x >= WIDTH - 50 or colidiu_parede(inimigo):
        inimigo.x = x_antigo
        direcao_investigacao = -1
        inimigo.y += 30
    elif inimigo.x <= 50 or colidiu_parede(inimigo):
        inimigo.x = x_antigo
        direcao_investigacao = 1
        inimigo.y += 30

    inimigo.x = max(50, min(WIDTH - 50, inimigo.x))
    inimigo.y = max(50, min(HEIGHT - 50, inimigo.y))


def reiniciar_jogo():
    global pontos, VIDA, estado_jogo, estado_inimigo
    pontos = 0
    VIDA = 3
    estado_jogo = "JOGANDO"
    estado_inimigo = "PATRULHANDO"
    heroi.pos = (400, 300)
    inimigo.pos = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
    posicionar_moeda()


def draw():
    screen.fill((0, 20, 255))

    if estado_jogo == "JOGANDO":
        cor_visao = (255, 50, 50) if estado_inimigo == "PERSEGUINDO" else (100, 100, 255)
        screen.draw.circle(inimigo.pos, RAIO_VISAO, cor_visao)

        for parede in paredes:
            screen.draw.filled_rect(parede, (120, 130, 150))
            screen.draw.rect(parede, "white")

        if estado_inimigo == "PERSEGUINDO":
            status_alerta = "ALERTA: INIMIGO TE VIU!"
            cor_texto = "crimson"
        else:
            status_alerta = "Status: Oculto"
            cor_texto = "lime"

        screen.draw.text(
            status_alerta,
            midbottom=(WIDTH // 2, HEIGHT - 15),
            fontsize=22,
            color=cor_texto
        )

        heroi.draw()
        inimigo.draw()
        Moeda.draw()

    elif estado_jogo == "VITORIA":
        screen.draw.text(
            "VOCÊ ESCAPOU COM SUCESSO!",
            center=(WIDTH // 2, 250),
            fontsize=50,
            color="gold"
        )
        screen.draw.text(
            "Pressione [R] para jogar novamente",
            center=(WIDTH // 2, 350),
            fontsize=30,
            color="white"
        )

    elif estado_jogo == "GAMEOVER":
        screen.draw.text(
            "GAME OVER",
            center=(WIDTH // 2, 220),
            fontsize=64,
            color="crimson",
            shadow=(2, 2),
            scolor="black"
        )
        screen.draw.text(
            "Pressione [R] para reiniciar",
            center=(WIDTH // 2, 320),
            fontsize=30,
            color="white"
        )

    screen.draw.text(
        f"Pontos: {pontos}/{PONTOS_VITORIA} | Vidas: {VIDA}",
        topleft=(20, 20),
        fontsize=32,
        color="white",
        shadow=(1, 1),
        scolor="black"
    )


def update(dt):
    global pontos, estado_inimigo, tempo_sem_ver, ultima_posicao_heroi, estado_jogo, VIDA

    if estado_jogo in ["VITORIA", "GAMEOVER"]:
        if keyboard.r:
            reiniciar_jogo()
        return

    if keyboard.right:
        heroi.x += 3
        if colidiu_parede(heroi):
            heroi.x -= 3
    if keyboard.left:
        heroi.x -= 3
        if colidiu_parede(heroi):
            heroi.x += 3
    if keyboard.up:
        heroi.y -= 3
        if colidiu_parede(heroi):
            heroi.y += 3
    if keyboard.down:
        heroi.y += 3
        if colidiu_parede(heroi):
            heroi.y -= 3

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
                    x_antigo = inimigo.x
                    inimigo.x += (dx / dist) * 2
                    if colidiu_parede(inimigo):
                        inimigo.x = x_antigo

                    y_antigo = inimigo.y
                    inimigo.y += (dy / dist) * 2
                    if colidiu_parede(inimigo):
                        inimigo.y = y_antigo

            if tempo_sem_ver >= TEMPO_INVESTIGACAO:
                estado_inimigo = "INVESTIGANDO"
                tempo_sem_ver = 0

        elif estado_inimigo == "INVESTIGANDO":
            investigar()
        else:
            estado_inimigo = "PATRULHANDO"
            patrulhar()

    if heroi.colliderect(Moeda):
        pontos += 1
        posicionar_moeda()

        if pontos >= PONTOS_VITORIA:
            estado_jogo = "VITORIA"

    if inimigo.colliderect(heroi):
        VIDA -= 1
        heroi.x = 400
        heroi.y = 300

        if VIDA <= 0:
            estado_jogo = "GAMEOVER"


pgzrun.go()