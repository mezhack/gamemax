import math
import random
import sys

import pygame


pygame.init()

LARGURA = 800
ALTURA = 600
FPS = 60

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Operação Stealth")
relogio = pygame.time.Clock()

fonte = pygame.font.SysFont("arial", 22, True)
fonte_menor = pygame.font.SysFont("arial", 16, True)

FUNDO = (20, 20, 25)
BRANCO = (245, 245, 245)
VERDE = (50, 220, 100)
VERMELHO = (230, 55, 55)
ROXO = (185, 75, 225)
AMARELO = (255, 215, 0)
AZUL = (55, 135, 240)
LARANJA = (245, 150, 45)
CIANO = (40, 220, 220)
CINZA = (95, 100, 115)
BORDA = (170, 175, 190)

paredes = [
    pygame.Rect(170, 100, 30, 210),
    pygame.Rect(260, 270, 250, 30),
    pygame.Rect(500, 100, 30, 200),
    pygame.Rect(410, 420, 250, 30),
]

jogador = pygame.Rect(0, 0, 24, 24)
chave = pygame.Rect(0, 0, 16, 16)
porta = pygame.Rect(0, 0, 34, 45)
moeda = pygame.Rect(0, 0, 16, 16)
turbo = pygame.Rect(0, 0, 15, 15)

pontos = 0
vidas = 3
pegou_chave = False
estado = "JOGANDO"
tempo_para_mudar = 50.0
tempo_turbo = 0.0


def colide_parede(objeto):
    return any(objeto.colliderect(parede) for parede in paredes)


def andar(objeto, dx, dy):
    distancia = math.hypot(dx, dy)
    passos = max(1, int(distancia / 2) + 1)

    for _ in range(passos):
        passo_x = dx / passos
        passo_y = dy / passos

        objeto.x += round(passo_x)
        if colide_parede(objeto):
            objeto.x -= round(passo_x)

        objeto.y += round(passo_y)
        if colide_parede(objeto):
            objeto.y -= round(passo_y)

    objeto.left = max(0, objeto.left)
    objeto.right = min(LARGURA, objeto.right)
    objeto.top = max(48, objeto.top)
    objeto.bottom = min(ALTURA, objeto.bottom)


def escolher_local(tamanho, longe_de=None, distancia=0):
    for _ in range(2000):
        tentativa = pygame.Rect(
            random.randint(25, LARGURA - tamanho - 25),
            random.randint(65, ALTURA - tamanho - 25),
            tamanho,
            tamanho,
        )

        if colide_parede(tentativa):
            continue

        if longe_de is not None:
            diferenca_x = tentativa.centerx - longe_de[0]
            diferenca_y = tentativa.centery - longe_de[1]
            if math.hypot(diferenca_x, diferenca_y) < distancia:
                continue

        return tentativa.center

    return 60, 70


def jogador_visivel(inimigo):
    dx = jogador.centerx - inimigo["corpo"].centerx
    dy = jogador.centery - inimigo["corpo"].centery
    distancia = math.hypot(dx, dy)

    if distancia > 260:
        return False
    if distancia == 0:
        return True

    quantidade = max(2, int(distancia / 4))
    for numero in range(1, quantidade):
        parte = numero / quantidade
        x = inimigo["corpo"].centerx + dx * parte
        y = inimigo["corpo"].centery + dy * parte
        if any(parede.collidepoint(x, y) for parede in paredes):
            return False
    return True


def novo_inimigo(nome, cor, rota, velocidade):
    return {
        "nome": nome,
        "cor": cor,
        "rota": rota,
        "velocidade": velocidade,
        "corpo": pygame.Rect(0, 0, 22, 22),
        "alvo": 0,
        "estado": "PATRULHA",
        "espera": 0,
        "ultima_posicao": None,
    }


def colocar_inimigo(inimigo, posicao):
    inimigo["corpo"].center = posicao
    inimigo["alvo"] = 0
    inimigo["estado"] = "PATRULHA"
    inimigo["espera"] = 0
    inimigo["ultima_posicao"] = None


def mover_inimigo(inimigo, destino, velocidade, tempo):
    corpo = inimigo["corpo"]
    diferenca_x = destino[0] - corpo.centerx
    diferenca_y = destino[1] - corpo.centery
    distancia = math.hypot(diferenca_x, diferenca_y)

    if distancia < 7:
        return True

    andar(
        corpo,
        diferenca_x / distancia * velocidade * tempo,
        diferenca_y / distancia * velocidade * tempo,
    )
    return False


def atualizar_inimigo(inimigo, tempo):
    viu = jogador_visivel(inimigo)

    if viu:
        inimigo["estado"] = "PERSEGUINDO"
        inimigo["ultima_posicao"] = jogador.center

    elif inimigo["estado"] == "PERSEGUINDO":
        inimigo["estado"] = "ESPERA"
        inimigo["espera"] = 1.5
        if inimigo["ultima_posicao"] is None:
            inimigo["ultima_posicao"] = inimigo["corpo"].center

    if inimigo["estado"] == "PERSEGUINDO":
        mover_inimigo(
            inimigo,
            jogador.center,
            inimigo["velocidade"] + 18,
            tempo,
        )
        return

    if inimigo["estado"] == "ESPERA":
        chegou = mover_inimigo(
            inimigo,
            inimigo["ultima_posicao"],
            inimigo["velocidade"],
            tempo,
        )
        if chegou:
            inimigo["espera"] -= tempo
        if inimigo["espera"] <= 0:
            inimigo["estado"] = "PATRULHA"
            inimigo["alvo"] += 1
            if inimigo["alvo"] == len(inimigo["rota"]):
                inimigo["alvo"] = 0
        return

    ponto = inimigo["rota"][inimigo["alvo"]]
    chegou = mover_inimigo(inimigo, ponto, inimigo["velocidade"], tempo)
    if chegou:
        inimigo["alvo"] += 1
        if inimigo["alvo"] == len(inimigo["rota"]):
            inimigo["alvo"] = 0


def desenhar_inimigo(inimigo):
    corpo = inimigo["corpo"]
    pygame.draw.rect(tela, inimigo["cor"], corpo)
    pygame.draw.rect(tela, BRANCO, corpo, 1)
    tela.blit(fonte_menor.render(inimigo["nome"], True, BRANCO),
              (corpo.x + 4, corpo.y + 2))

    if inimigo["estado"] == "PERSEGUINDO":
        tela.blit(fonte.render("!", True, VERMELHO),
                  (corpo.centerx - 5, corpo.y - 25))
    elif inimigo["estado"] == "ESPERA":
        tela.blit(fonte_menor.render("?", True, AMARELO),
                  (corpo.centerx - 4, corpo.y - 20))


def mudar_objetivos():
    global pegou_chave, tempo_para_mudar

    chave.center = escolher_local(chave.width, jogador.center, 80)
    porta.center = escolher_local(porta.width, chave.center, 140)
    pegou_chave = False
    tempo_para_mudar = 50.0


def reiniciar():
    global pontos, vidas, pegou_chave, estado, tempo_para_mudar, tempo_turbo

    jogador.center = escolher_local(jogador.width)
    chave.center = escolher_local(chave.width, jogador.center, 100)
    porta.center = escolher_local(porta.width, chave.center, 150)
    moeda.center = escolher_local(moeda.width, jogador.center, 70)
    turbo.center = escolher_local(turbo.width, jogador.center, 100)

    colocar_inimigo(inimigo_1, escolher_local(22, jogador.center, 180))
    colocar_inimigo(inimigo_2, escolher_local(22, jogador.center, 180))

    pontos = 0
    vidas = 3
    pegou_chave = False
    estado = "JOGANDO"
    tempo_para_mudar = 50.0
    tempo_turbo = 0


def controlar_jogador(tempo):
    teclas = pygame.key.get_pressed()
    x = 0
    y = 0

    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        x -= 1
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        x += 1
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
        y -= 1
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
        y += 1

    if x == 0 and y == 0:
        return

    tamanho = math.hypot(x, y)
    velocidade = 240 if tempo_turbo > 0 else 150
    andar(jogador, x / tamanho * velocidade * tempo,
          y / tamanho * velocidade * tempo)


rota_1 = [(70, 80), (70, 360), (350, 360), (350, 80)]
rota_2 = [(700, 80), (700, 350), (560, 350), (700, 520)]
inimigo_1 = novo_inimigo("G1", VERMELHO, rota_1, 65)
inimigo_2 = novo_inimigo("G2", ROXO, rota_2, 58)

reiniciar()

while True:
    tempo = relogio.tick(FPS) / 1000

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            reiniciar()

    if estado == "JOGANDO":
        controlar_jogador(tempo)
        tempo_para_mudar -= tempo

        if tempo_para_mudar <= 0:
            mudar_objetivos()

        if tempo_turbo > 0:
            tempo_turbo -= tempo

        if not pegou_chave and jogador.colliderect(chave):
            pegou_chave = True
            pontos += 2

        if jogador.colliderect(moeda):
            pontos += 1
            moeda.center = escolher_local(moeda.width, jogador.center, 80)

        if jogador.colliderect(turbo):
            pontos += 2
            tempo_turbo = 5
            turbo.center = escolher_local(turbo.width, jogador.center, 100)

        atualizar_inimigo(inimigo_1, tempo)
        atualizar_inimigo(inimigo_2, tempo)

        if (jogador.colliderect(inimigo_1["corpo"]) or
                jogador.colliderect(inimigo_2["corpo"])):
            vidas -= 1
            pontos = max(0, pontos - 1)

            if vidas <= 0:
                vidas = 0
                estado = "GAMEOVER"
            else:
                jogador.center = escolher_local(jogador.width)
                colocar_inimigo(inimigo_1, escolher_local(22, jogador.center, 180))
                colocar_inimigo(inimigo_2, escolher_local(22, jogador.center, 180))

        if pegou_chave and jogador.colliderect(porta):
            estado = "VITORIA"

    tela.fill(FUNDO)

    for parede in paredes:
        pygame.draw.rect(tela, CINZA, parede)
        pygame.draw.rect(tela, BORDA, parede, 2)

    pygame.draw.rect(tela, AZUL, porta)
    if not pegou_chave:
        pygame.draw.rect(tela, AMARELO, chave)
    pygame.draw.ellipse(tela, LARANJA, moeda)
    pygame.draw.rect(tela, CIANO, turbo)
    pygame.draw.rect(tela, BRANCO, jogador)
    pygame.draw.rect(tela, VERDE, jogador.inflate(-2, -2))

    desenhar_inimigo(inimigo_1)
    desenhar_inimigo(inimigo_2)

    texto = "Chave: OK" if pegou_chave else "Chave: Pendente"
    tela.blit(fonte.render(texto, True, BRANCO), (15, 12))
    tela.blit(fonte.render(f"Pontos: {pontos}", True, AMARELO), (215, 12))
    tela.blit(fonte.render(f"Vidas: {vidas}", True, VERMELHO), (380, 12))
    tela.blit(fonte_menor.render(f"Mudança da chave: {max(0, int(tempo_para_mudar))}s", True, BRANCO), (520, 16))
    tela.blit(fonte_menor.render("Ciano: turbo | WASD/setas: mover | R: reiniciar", True, BRANCO), (15, 575))

    if tempo_turbo > 0:
        tela.blit(fonte_menor.render("TURBO ATIVO", True, CIANO), (520, 38))

    if estado == "GAMEOVER":
        tela.blit(fonte.render("GAME OVER - pressione R", True, VERMELHO), (270, 290))
    elif estado == "VITORIA":
        tela.blit(fonte.render("VOCÊ VENCEU - pressione R", True, VERDE), (270, 290))

    pygame.display.flip()
    