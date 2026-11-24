import math
import random
import sys

import pygame


pygame.init()

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Operação Stealth")
relogio = pygame.time.Clock()

fonte = pygame.font.SysFont("arial", 22, bold=True)
fonte_pequena = pygame.font.SysFont("arial", 16, bold=True)


PRETO = (20, 20, 25)
BRANCO = (245, 245, 245)
VERDE_HEROI = (50, 220, 100)
VERMELHO = (230, 55, 55)
ROXO = (185, 75, 225)
AMARELO = (255, 215, 0)
AZUL = (55, 135, 240)
LARANJA = (245, 150, 45)
CINZA_PAREDE = (95, 100, 115)
BORDA_PAREDE = (170, 175, 190)


paredes = [
    pygame.Rect(170, 100, 30, 210),
    pygame.Rect(260, 270, 250, 30),
    pygame.Rect(500, 100, 30, 200),
    pygame.Rect(410, 420, 250, 30),
]


def bateu_na_parede(retangulo):
    return any(retangulo.colliderect(parede) for parede in paredes)


def mover_com_colisao(retangulo, dx, dy):
    distancia = math.hypot(dx, dy)
    passos = max(1, int(distancia / 2) + 1)
    passo_x = dx / passos
    passo_y = dy / passos

    for _ in range(passos):
        retangulo.x += round(passo_x)
        if bateu_na_parede(retangulo):
            retangulo.x -= round(passo_x)

        retangulo.y += round(passo_y)
        if bateu_na_parede(retangulo):
            retangulo.y -= round(passo_y)


    retangulo.left = max(0, retangulo.left)
    retangulo.right = min(LARGURA, retangulo.right)
    retangulo.top = max(45, retangulo.top)
    retangulo.bottom = min(ALTURA, retangulo.bottom)


def tem_linha_de_visao(origem, alvo):
    distancia = math.hypot(alvo.centerx - origem.centerx,
                            alvo.centery - origem.centery)
    passos = max(1, int(distancia / 4))

    for passo in range(1, passos):
        fator = passo / passos
        x = origem.centerx + (alvo.centerx - origem.centerx) * fator
        y = origem.centery + (alvo.centery - origem.centery) * fator
        if any(parede.collidepoint(x, y) for parede in paredes):
            return False
    return True


def posicao_livre(tamanho, evitar=None, distancia_minima=0):
    for _ in range(2000):
        candidato = pygame.Rect(
            random.randint(25, LARGURA - tamanho - 25),
            random.randint(65, ALTURA - tamanho - 25),
            tamanho,
            tamanho,
        )
        if bateu_na_parede(candidato):
            continue
        if evitar is not None and math.hypot(
            candidato.centerx - evitar[0], candidato.centery - evitar[1]
        ) < distancia_minima:
            continue
        return candidato.center

    return (60, 70)


class Inimigo:

    def __init__(self, nome, cor, pontos_de_rota, velocidade):
        self.nome = nome
        self.cor = cor
        self.rect = pygame.Rect(0, 0, 22, 22)
        self.velocidade = velocidade
        self.velocidade_perseguicao = velocidade + 18
        self.rota = pontos_de_rota
        self.indice_rota = 0
        self.estado = "PATRULHA"
        self.tempo_espera = 0
        self.tempo_sem_ver = 0

    def reiniciar(self, posicao):
        self.rect.center = posicao
        self.indice_rota = 0
        self.estado = "PATRULHA"
        self.tempo_espera = 0
        self.tempo_sem_ver = 0

    def detectou(self, heroi):
        distancia = math.hypot(
            heroi.centerx - self.rect.centerx,
            heroi.centery - self.rect.centery,
        )
        return distancia <= 260 and tem_linha_de_visao(self.rect, heroi)

    def seguir_ponto(self, ponto, velocidade, dt):
        dx = ponto[0] - self.rect.centerx
        dy = ponto[1] - self.rect.centery
        distancia = math.hypot(dx, dy)

        if distancia < 7:
            return True

        mover_com_colisao(
            self.rect,
            dx / distancia * velocidade * dt,
            dy / distancia * velocidade * dt,
        )
        return False

    def atualizar(self, heroi, dt):
        viu_o_heroi = self.detectou(heroi)

        if viu_o_heroi:
            self.estado = "PERSEGUINDO"
            self.tempo_sem_ver = 0

        elif self.estado == "PERSEGUINDO":

            self.estado = "ESPERA"
            self.tempo_espera = 1.5
            self.tempo_sem_ver = 0

        if self.estado == "PERSEGUINDO":
            self.seguir_ponto(heroi.center, self.velocidade_perseguicao, dt)

        elif self.estado == "ESPERA":
            self.tempo_espera -= dt
            if self.tempo_espera <= 0:
                self.estado = "PATRULHA"
                self.indice_rota = (self.indice_rota + 1) % len(self.rota)

        else:
            destino = self.rota[self.indice_rota]
            chegou = self.seguir_ponto(destino, self.velocidade, dt)
            if chegou:
                self.indice_rota = (self.indice_rota + 1) % len(self.rota)

    def desenhar(self):
        pygame.draw.rect(tela, self.cor, self.rect)
        pygame.draw.rect(tela, BRANCO, self.rect, 1)
        etiqueta = fonte_pequena.render(self.nome, True, BRANCO)
        tela.blit(etiqueta, (self.rect.x + 4, self.rect.y + 2))

        if self.estado == "PERSEGUINDO":
            alerta = fonte.render("!", True, VERMELHO)
            tela.blit(alerta, (self.rect.centerx - 5, self.rect.y - 25))
        elif self.estado == "ESPERA":
            alerta = fonte_pequena.render("?", True, AMARELO)
            tela.blit(alerta, (self.rect.centerx - 4, self.rect.y - 20))


rota_g1 = [(70, 80), (70, 360), (350, 360), (350, 80)]
rota_g2 = [(700, 80), (700, 350), (560, 350), (700, 520)]

guarda = Inimigo("G1", VERMELHO, rota_g1, 65)
guarda_2 = Inimigo("G2", ROXO, rota_g2, 58)


heroi = pygame.Rect(0, 0, 24, 24)
chave = pygame.Rect(0, 0, 16, 16)
porta = pygame.Rect(0, 0, 34, 45)
moeda = pygame.Rect(0, 0, 16, 16)

pegou_chave = False
pontos = 0
vidas = 3
status_jogo = "JOGANDO"


def reiniciar_jogo(resetar_pontuacao=True):
    global pegou_chave, pontos, vidas, status_jogo

    inicio = posicao_livre(heroi.width)
    heroi.center = inicio
    chave.center = posicao_livre(chave.width, inicio, 100)
    porta.center = posicao_livre(porta.width, chave.center, 150)
    moeda.center = posicao_livre(moeda.width, inicio, 70)

    guarda.reiniciar(posicao_livre(guarda.rect.width, inicio, 180))
    guarda_2.reiniciar(posicao_livre(guarda_2.rect.width, inicio, 180))

    pegou_chave = False
    status_jogo = "JOGANDO"
    vidas = 3
    if resetar_pontuacao:
        pontos = 0


def reaparecer_apos_ser_pego():
    global vidas, status_jogo, pontos

    vidas -= 1
    pontos = max(0, pontos - 1)

    if vidas <= 0:
        vidas = 0
        status_jogo = "GAMEOVER"
        return

    nova_posicao = posicao_livre(heroi.width)
    heroi.center = nova_posicao
    guarda.reiniciar(posicao_livre(guarda.rect.width, nova_posicao, 180))
    guarda_2.reiniciar(posicao_livre(guarda_2.rect.width, nova_posicao, 180))


def atualizar_movimento_heroi(dt):
    teclas = pygame.key.get_pressed()
    dx = int(teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) - int(
        teclas[pygame.K_LEFT] or teclas[pygame.K_a]
    )
    dy = int(teclas[pygame.K_DOWN] or teclas[pygame.K_s]) - int(
        teclas[pygame.K_UP] or teclas[pygame.K_w]
    )

    if dx or dy:
        tamanho = math.hypot(dx, dy)
        mover_com_colisao(
            heroi,
            dx / tamanho * 150 * dt,
            dy / tamanho * 150 * dt,
        )


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
        atualizar_movimento_heroi(dt)

        if not pegou_chave and heroi.colliderect(chave):
            pegou_chave = True
            pontos += 2

        if heroi.colliderect(moeda):
            pontos += 1
            moeda.center = posicao_livre(moeda.width, heroi.center, 80)

        guarda.atualizar(heroi, dt)
        guarda_2.atualizar(heroi, dt)

        if heroi.colliderect(guarda.rect) or heroi.colliderect(guarda_2.rect):
            reaparecer_apos_ser_pego()
        elif pegou_chave and heroi.colliderect(porta):
            status_jogo = "VITORIA"


    tela.fill(PRETO)

    for parede in paredes:
        pygame.draw.rect(tela, CINZA_PAREDE, parede)
        pygame.draw.rect(tela, BORDA_PAREDE, parede, 2)

    pygame.draw.rect(tela, AZUL, porta)
    if not pegou_chave:
        pygame.draw.rect(tela, AMARELO, chave)
    pygame.draw.ellipse(tela, LARANJA, moeda)
    pygame.draw.rect(tela, VERDE_HEROI, heroi)
    pygame.draw.rect(tela, BRANCO, heroi, 1)

    guarda.desenhar()
    guarda_2.desenhar()

    texto_chave = "Chave: OK" if pegou_chave else "Chave: Pendente"
    tela.blit(fonte.render(texto_chave, True, BRANCO), (15, 12))
    tela.blit(fonte.render(f"Pontos: {pontos}", True, AMARELO), (215, 12))
    tela.blit(fonte.render(f"Vidas: {vidas}", True, VERMELHO), (380, 12))
    tela.blit(fonte_pequena.render("WASD/setas: mover | R: reiniciar", True, BRANCO), (15, ALTURA - 25))

    if status_jogo == "GAMEOVER":
        mensagem = fonte.render("GAME OVER - pressione R para reiniciar", True, VERMELHO)
        tela.blit(mensagem, (210, ALTURA // 2))
    elif status_jogo == "VITORIA":
        mensagem = fonte.render("VOCÊ VENCEU! - pressione R para jogar", True, VERDE_HEROI)
        tela.blit(mensagem, (215, ALTURA // 2))

    pygame.display.flip()
