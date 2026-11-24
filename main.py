
import pygame
import sys
import math

# Inicialização
pygame.init()
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Operação Stealth - Edição Colaborativa")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("arial", 24, bold=True)

# Cores (R, G, B)
PRETO = (20, 20, 25)
VERDE_HEROI = (50, 220, 100)
VERMELHO_GUARDA = (230, 50, 50)
AMARELO_CHAVE = (255, 215, 0)
AZUL_PORTA = (50, 130, 240)
CINZA_PAREDE = (100, 100, 110)
BRANCO = (255, 255, 255)

# Entidades do Jogo
heroi = pygame.Rect(60, 60, 35, 35)
velocidade_heroi = 5

ladrão = pygame.Rect(180, 60, 40, 40)
velocidade_ladrao = 3

guarda = pygame.Rect(380, 250, 40, 40)
velocidade_guarda = 4
direcao_guarda = 1  # 1 = desce, -1 = sobe

chave = pygame.Rect(700, 80, 20, 20)
porta = pygame.Rect(720, 500, 45, 65)

# Obstáculos
obstaculos = [
    pygame.Rect(260, 170, 35, 220),
    pygame.Rect(470, 300, 35, 200),
    pygame.Rect(540, 180, 130, 30)
]

# Configurações do ladrão
RAIO_VISAO = 200

pontos_patrulha = [
    (100, 120),
    (700, 120),
    (700, 520),
    (100, 520)
]

ponto_atual = 0

# Estados do Jogo
pegou_chave = False
status_jogo = "JOGANDO"


# Verifica se o ladrão consegue enxergar o herói
def enxerga_heroi(ladrao, heroi):

    diferenca_x = heroi.centerx - ladrao.centerx
    diferenca_y = heroi.centery - ladrao.centery

    distancia = math.sqrt(diferenca_x**2 + diferenca_y**2)

    if distancia > RAIO_VISAO:
        return False

    for parede in obstaculos:
        if parede.clipline(ladrao.center, heroi.center):
            return False

    return True


# Movimenta um personagem sem permitir que atravesse paredes
def mover_com_colisao(personagem, movimento_x, movimento_y):

    personagem.x += round(movimento_x)

    for parede in obstaculos:
        if personagem.colliderect(parede):

            if movimento_x > 0:
                personagem.right = parede.left

            elif movimento_x < 0:
                personagem.left = parede.right

    personagem.y += round(movimento_y)

    for parede in obstaculos:
        if personagem.colliderect(parede):

            if movimento_y > 0:
                personagem.bottom = parede.top

            elif movimento_y < 0:
                personagem.top = parede.bottom


# Movimentação e patrulha do ladrão
def movimentar_ladrao():

    global ponto_atual

    if enxerga_heroi(ladrão, heroi):

        destino_x = heroi.x
        destino_y = heroi.y

    else:

        destino_x, destino_y = pontos_patrulha[ponto_atual]

        distancia_ponto = math.sqrt(
            (destino_x - ladrão.x)**2 +
            (destino_y - ladrão.y)**2
        )

        if distancia_ponto < 5:

            ponto_atual = (ponto_atual + 1) % len(pontos_patrulha)

            destino_x, destino_y = pontos_patrulha[ponto_atual]

    diferenca_x = destino_x - ladrão.x
    diferenca_y = destino_y - ladrão.y

    distancia = math.sqrt(diferenca_x**2 + diferenca_y**2)

    if distancia > 0:

        movimento_x = (diferenca_x / distancia) * velocidade_ladrao
        movimento_y = (diferenca_y / distancia) * velocidade_ladrao

        mover_com_colisao(ladrão, movimento_x, movimento_y)

    # Mantém o ladrão dentro da tela
    ladrão.x = max(0, min(LARGURA - ladrão.width, ladrão.x))
    ladrão.y = max(0, min(ALTURA - ladrão.height, ladrão.y))


while True:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Reiniciar com a tecla R
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:

            heroi.topleft = (60, 60)
            ladrão.topleft = (180, 60)
            ponto_atual = 0

            pegou_chave = False
            status_jogo = "JOGANDO"

    if status_jogo == "JOGANDO":

        # Movimentação do Herói
        teclas = pygame.key.get_pressed()
        dx, dy = 0, 0

        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx = -velocidade_heroi

        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx = velocidade_heroi

        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            dy = -velocidade_heroi

        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            dy = velocidade_heroi

        # Atualiza posição do herói com colisões
        mover_com_colisao(heroi, dx, dy)

        # Mantém dentro da tela
        heroi.x = max(0, min(LARGURA - heroi.width, heroi.x))
        heroi.y = max(0, min(ALTURA - heroi.height, heroi.y))

        # Patrulha vertical do Guarda
        guarda.y += velocidade_guarda * direcao_guarda

        if guarda.top <= 40 or guarda.bottom >= ALTURA - 40:
            direcao_guarda *= -1

        # Movimentação do ladrão
        movimentar_ladrao()

        # Colisões
        if not pegou_chave and heroi.colliderect(chave):
            pegou_chave = True

        if heroi.colliderect(guarda):
            status_jogo = "PERDEU"

        # Assalto do ladrão
        if heroi.colliderect(ladrão):
            status_jogo = "PERDEU"

        if pegou_chave and heroi.colliderect(porta):
            status_jogo = "VENCEU"

    # Renderização
    tela.fill(PRETO)

    # Desenha Porta e Chave
    pygame.draw.rect(tela, AZUL_PORTA, porta)

    if not pegou_chave:
        pygame.draw.rect(tela, AMARELO_CHAVE, chave)

    # Desenha Obstáculos
    for parede in obstaculos:
        pygame.draw.rect(tela, CINZA_PAREDE, parede)

    # Desenha campo de visão do ladrão
    pygame.draw.circle(
        tela,
        (100, 100, 100),
        (ladrão.centerx, ladrão.centery),
        RAIO_VISAO,
        1
    )

    # Desenha Herói, Guarda e Ladrão
    pygame.draw.rect(tela, VERDE_HEROI, heroi)
    pygame.draw.rect(tela, VERMELHO_GUARDA, guarda)
    pygame.draw.rect(tela, (150, 50, 200), ladrão)

    # HUD / Interface
    texto_chave = "Chave: OK!" if pegou_chave else "Chave: Pendente"
    hud = fonte.render(texto_chave, True, BRANCO)
    tela.blit(hud, (20, 15))

    if status_jogo == "PERDEU":

        msg = fonte.render(
            "CAPTURADO! Pressione R para tentar novamente.",
            True,
            VERMELHO_GUARDA
        )

        tela.blit(msg, (140, ALTURA // 2))

    elif status_jogo == "VENCEU":

        msg = fonte.render(
            "ESCAPOU COM SUCESSO! Pressione R para jogar.",
            True,
            VERDE_HEROI
        )

        tela.blit(msg, (140, ALTURA // 2))

    pygame.display.flip()
    relogio.tick(60)
