import math
import random
import sys

import pygame


pygame.init()

LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Operação Stealth")
relogio = pygame.time.Clock()

fonte = pygame.font.SysFont("arial", 22, bold=True)
fonte_pequena = pygame.font.SysFont("arial", 16, bold=True)

PRETO = (20, 20, 25)
BRANCO = (245, 245, 245)
VERDE = (50, 220, 100)
VERMELHO = (230, 55, 55)
ROXO = (185, 75, 225)
AMARELO = (255, 215, 0)
AZUL = (55, 135, 240)
LARANJA = (245, 150, 45)
CINZA = (95, 100, 115)
CINZA_CLARO = (170, 175, 190)

paredes = [
    pygame.Rect(170, 100, 30, 210),
    pygame.Rect(260, 270, 250, 30),
    pygame.Rect(500, 100, 30, 200),
    pygame.Rect(410, 420, 250, 30),
]


def esta_na_parede(objeto):
    for parede in paredes:
        if objeto.colliderect(parede):
            return True
    return False


def mover(objeto, x, y):
    distancia = math.hypot(x, y)
    quantidade = max(1, int(distancia / 2) + 1)
    passo_x = x / quantidade
    passo_y = y / quantidade

    for _ in range(quantidade):
        objeto.x += round(passo_x)
        if esta_na_parede(objeto):
            objeto.x -= round(passo_x)

        objeto.y += round(passo_y)
        if esta_na_parede(objeto):
            objeto.y -= round(passo_y)

    if objeto.left < 0:
        objeto.left = 0
    if objeto.right > LARGURA:
        objeto.right = LARGURA
    if objeto.top < 48:
        objeto.top = 48
    if objeto.bottom > ALTURA:
        objeto.bottom = ALTURA


def pode_ver(primeiro, segundo):
    distancia_x = segundo.centerx - primeiro.centerx
    distancia_y = segundo.centery - primeiro.centery
    distancia = math.hypot(distancia_x, distancia_y)

    if distancia > 260:
        return False
    if distancia == 0:
        return True

    passos = max(1, int(distancia / 4))
    for numero in range(1, passos):
        parte = numero / passos
        x = primeiro.centerx + distancia_x * parte
        y = primeiro.centery + distancia_y * parte
        for parede in paredes:
            if parede.collidepoint(x, y):
                return False
    return True


def lugar_livre(tamanho, evitar=None, distancia=0):
    for _ in range(2000):
        novo = pygame.Rect(
            random.randint(25, LARGURA - tamanho - 25),
            random.randint(65, ALTURA - tamanho - 25),
            tamanho,
            tamanho,
        )

        if esta_na_parede(novo):
            continue

        if evitar is not None:
            distancia_x = novo.centerx - evitar[0]
            distancia_y = novo.centery - evitar[1]
            if math.hypot(distancia_x, distancia_y) < distancia:
                continue

        return novo.center

    return 60, 70


class Inimigo:
    def __init__(self, nome, cor, caminho, velocidade):
        self.nome = nome
        self.cor = cor
        self.caminho = caminho
        self.velocidade = velocidade
        self.rect = pygame.Rect(0, 0, 22, 22)
        self.ponto_atual = 0
        self.estado = "PATRULHA"
        self.tempo_espera = 0
        self.local_visto = None

    def colocar(self, posicao):
        self.rect.center = posicao
        self.ponto_atual = 0
        self.estado = "PATRULHA"
        self.tempo_espera = 0
        self.local_visto = None

    def seguir(self, destino, velocidade, tempo):
        diferenca_x = destino[0] - self.rect.centerx
        diferenca_y = destino[1] - self.rect.centery
        distancia = math.hypot(diferenca_x, diferenca_y)

        if distancia < 7:
            return True

        mover(
            self.rect,
            diferenca_x / distancia * velocidade * tempo,
            diferenca_y / distancia * velocidade * tempo,
        )
        return False

    def atualizar(self, jogador, tempo):
        jogador_visivel = pode_ver(self.rect, jogador)

        if jogador_visivel:
            self.estado = "PERSEGUINDO"
            self.local_visto = jogador.center

        elif self.estado == "PERSEGUINDO":
            self.estado = "ESPERA"
            self.tempo_espera = 1.5
            if self.local_visto is None:
                self.local_visto = self.rect.center

        if self.estado == "PERSEGUINDO":
            self.seguir(jogador.center, self.velocidade + 18, tempo)

        elif self.estado == "ESPERA":
            chegou = self.seguir(self.local_visto, self.velocidade, tempo)
            if chegou:
                self.tempo_espera -= tempo
            if self.tempo_espera <= 0:
                self.estado = "PATRULHA"
                self.ponto_atual += 1
                if self.ponto_atual >= len(self.caminho):
                    self.ponto_atual = 0

        else:
            destino = self.caminho[self.ponto_atual]
            chegou = self.seguir(destino, self.velocidade, tempo)
            if chegou:
                self.ponto_atual += 1
                if self.ponto_atual >= len(self.caminho):
                    self.ponto_atual = 0

    def desenhar(self):
        pygame.draw.rect(tela, self.cor, self.rect)
        pygame.draw.rect(tela, BRANCO, self.rect, 1)
        tela.blit(fonte_pequena.render(self.nome, True, BRANCO),
                  (self.rect.x + 4, self.rect.y + 2))

        if self.estado == "PERSEGUINDO":
            tela.blit(fonte.render("!", True, VERMELHO),
                      (self.rect.centerx - 5, self.rect.y - 25))
        elif self.estado == "ESPERA":
            tela.blit(fonte_pequena.render("?", True, AMARELO),
                      (self.rect.centerx - 4, self.rect.y - 20))


jogador = pygame.Rect(0, 0, 24, 24)
chave = pygame.Rect(0, 0, 16, 16)
porta = pygame.Rect(0, 0, 34, 45)
moeda = pygame.Rect(0, 0, 16, 16)

inimigo_1 = Inimigo("G1", VERMELHO,
                    [(70, 80), (70, 360), (350, 360), (350, 80)], 65)
inimigo_2 = Inimigo("G2", ROXO,
                    [(700, 80), (700, 350), (560, 350), (700, 520)], 58)

pegou_chave = False
pontos = 0
vidas = 3
estado_jogo = "JOGANDO"


def reiniciar():
    global pegou_chave, pontos, vidas, estado_jogo

    jogador.center = lugar_livre(jogador.width)
    chave.center = lugar_livre(chave.width, jogador.center, 100)
    porta.center = lugar_livre(porta.width, chave.center, 150)
    moeda.center = lugar_livre(moeda.width, jogador.center, 70)

    inimigo_1.colocar(lugar_livre(inimigo_1.rect.width, jogador.center, 180))
    inimigo_2.colocar(lugar_livre(inimigo_2.rect.width, jogador.center, 180))

    pegou_chave = False
    pontos = 0
    vidas = 3
    estado_jogo = "JOGANDO"


def movimentar_jogador(tempo):
    teclas = pygame.key.get_pressed()
    horizontal = 0
    vertical = 0

    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        horizontal -= 1
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        horizontal += 1
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
        vertical -= 1
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
        vertical += 1

    if horizontal == 0 and vertical == 0:
        return

    tamanho = math.hypot(horizontal, vertical)
    mover(
        jogador,
        horizontal / tamanho * 150 * tempo,
        vertical / tamanho * 150 * tempo,
    )


def jogador_foi_pego():
    global vidas, pontos, estado_jogo

    vidas -= 1
    pontos = max(0, pontos - 1)

    if vidas <= 0:
        vidas = 0
        estado_jogo = "GAMEOVER"
    else:
        jogador.center = lugar_livre(jogador.width)
        inimigo_1.colocar(lugar_livre(inimigo_1.rect.width, jogador.center, 180))
        inimigo_2.colocar(lugar_livre(inimigo_2.rect.width, jogador.center, 180))


reiniciar()

while True:
    tempo = relogio.tick(60) / 1000

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            reiniciar()

    if estado_jogo == "JOGANDO":
        movimentar_jogador(tempo)

        if not pegou_chave and jogador.colliderect(chave):
            pegou_chave = True
            pontos += 2

        if jogador.colliderect(moeda):
            pontos += 1
            moeda.center = lugar_livre(moeda.width, jogador.center, 80)

        inimigo_1.atualizar(jogador, tempo)
        inimigo_2.atualizar(jogador, tempo)

        if jogador.colliderect(inimigo_1.rect) or jogador.colliderect(inimigo_2.rect):
            jogador_foi_pego()

        if pegou_chave and jogador.colliderect(porta):
            estado_jogo = "VITORIA"

    tela.fill(PRETO)

    for parede in paredes:
        pygame.draw.rect(tela, CINZA, parede)
        pygame.draw.rect(tela, CINZA_CLARO, parede, 2)

    pygame.draw.rect(tela, AZUL, porta)
    if not pegou_chave:
        pygame.draw.rect(tela, AMARELO, chave)
    pygame.draw.ellipse(tela, LARANJA, moeda)
    pygame.draw.rect(tela, VERDE, jogador)
    pygame.draw.rect(tela, BRANCO, jogador, 1)

    inimigo_1.desenhar()
    inimigo_2.desenhar()

    texto_chave = "Chave: OK" if pegou_chave else "Chave: Pendente"
    tela.blit(fonte.render(texto_chave, True, BRANCO), (15, 12))
    tela.blit(fonte.render(f"Pontos: {pontos}", True, AMARELO), (215, 12))
    tela.blit(fonte.render(f"Vidas: {vidas}", True, VERMELHO), (380, 12))
    tela.blit(fonte_pequena.render("WASD/setas: mover | R: reiniciar", True, BRANCO), (15, 575))

    if estado_jogo == "GAMEOVER":
        tela.blit(fonte.render("GAME OVER - pressione R", True, VERMELHO), (270, 290))
    elif estado_jogo == "VITORIA":
        tela.blit(fonte.render("VOCÊ VENCEU - pressione R", True, VERDE), (270, 290))

    pygame.display.flip()
