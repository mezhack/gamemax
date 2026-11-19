import pygame
import sys

# Inicialização
pygame.init()

LARGURA, ALTURA = 800, 600

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Operação Stealth - Edição Colaborativa")

relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("arial", 24, bold=True)

# Cores
PRETO = (20, 20, 25)
VERDE_HEROI = (50, 220, 100)
VERMELHO_GUARDA = (230, 50, 50)
AMARELO_CHAVE = (255, 215, 0)
AZUL_PORTA = (50, 130, 240)
CINZA_PAREDE = (100, 100, 110)
BRANCO = (255, 255, 255)

# Entidades do jogo
heroi = pygame.Rect(60, 60, 35, 35)
velocidade_heroi = 5

guarda = pygame.Rect(380, 250, 40, 40)
velocidade_guarda = 4
direcao_guarda = 1

chave = pygame.Rect(700, 80, 20, 20)
porta = pygame.Rect(720, 500, 45, 65)

# Mapa organizado com passagens ampliadas
obstaculos = [

    # Sala superior esquerda
    pygame.Rect(150, 0, 25, 140),
    pygame.Rect(150, 170, 130, 25),

    # Sala superior central-esquerda
    pygame.Rect(280, 70, 25, 140),
    pygame.Rect(175, 70, 105, 25),

    # Sala superior direita
    pygame.Rect(520, 0, 25, 170),
    pygame.Rect(545, 170, 130, 25),

    # Sala central esquerda
    pygame.Rect(70, 260, 25, 170),
    pygame.Rect(95, 260, 170, 25),
    pygame.Rect(265, 300, 25, 50),

    # Sala central direita
    pygame.Rect(510, 260, 170, 25),
    pygame.Rect(655, 285, 25, 100),

    # Sala inferior esquerda
    pygame.Rect(120, 420, 25, 180),
    pygame.Rect(145, 420, 140, 25),
    pygame.Rect(260, 470, 25, 75),

    # Sala inferior direita
    pygame.Rect(520, 420, 25, 180),
    pygame.Rect(545, 420, 130, 25),
    pygame.Rect(650, 445, 25, 100),

    # Divisões adicionais
    pygame.Rect(70, 120, 55, 25),
    pygame.Rect(680, 120, 70, 25),
    pygame.Rect(70, 500, 50, 25),
    pygame.Rect(680, 500, 70, 25),
]

# Estados do jogo
pegou_chave = False
status_jogo = "JOGANDO"

# Loop principal
while True:

    # Eventos
    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Reiniciar com R
        if evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_r:
                heroi.topleft = (60, 60)

                guarda.topleft = (380, 250)
                direcao_guarda = 1

                pegou_chave = False
                status_jogo = "JOGANDO"

    # Lógica do jogo
    if status_jogo == "JOGANDO":

        # Movimentação do herói
        teclas = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx = -velocidade_heroi

        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx = velocidade_heroi

        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            dy = -velocidade_heroi

        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            dy = velocidade_heroi

        # Colisão horizontal
        heroi.x += dx

        for parede in obstaculos:

            if heroi.colliderect(parede):

                if dx > 0:
                    heroi.right = parede.left

                elif dx < 0:
                    heroi.left = parede.right

        # Colisão vertical
        heroi.y += dy

        for parede in obstaculos:

            if heroi.colliderect(parede):

                if dy > 0:
                    heroi.bottom = parede.top

                elif dy < 0:
                    heroi.top = parede.bottom

        # Limites da tela
        heroi.x = max(0, min(LARGURA - heroi.width, heroi.x))
        heroi.y = max(0, min(ALTURA - heroi.height, heroi.y))

        # Patrulha do guarda
        guarda.y += velocidade_guarda * direcao_guarda

        if guarda.top <= 40 or guarda.bottom >= ALTURA - 40:
            direcao_guarda *= -1

        # Pegar chave
        if not pegou_chave and heroi.colliderect(chave):
            pegou_chave = True

        # Colisão com o guarda
        if heroi.colliderect(guarda):
            status_jogo = "PERDEU"

        # Entrar na porta
        if pegou_chave and heroi.colliderect(porta):
            status_jogo = "VENCEU"

    # Renderização
    tela.fill(PRETO)

    # Porta
    pygame.draw.rect(tela, AZUL_PORTA, porta)

    # Chave
    if not pegou_chave:
        pygame.draw.rect(tela, AMARELO_CHAVE, chave)

    # Paredes
    for parede in obstaculos:
        pygame.draw.rect(tela, CINZA_PAREDE, parede)

    # Herói e guarda
    pygame.draw.rect(tela, VERDE_HEROI, heroi)
    pygame.draw.rect(tela, VERMELHO_GUARDA, guarda)

    # Interface
    texto_chave = "Chave: OK!" if pegou_chave else "Chave: Pendente"

    hud = fonte.render(texto_chave, True, BRANCO)
    tela.blit(hud, (20, 15))

    # Mensagem de derrota
    if status_jogo == "PERDEU":

        msg = fonte.render(
            "CAPTURADO! Pressione R para tentar novamente.",
            True,
            VERMELHO_GUARDA
        )

        tela.blit(msg, (100, ALTURA // 2))

    # Mensagem de vitória
    elif status_jogo == "VENCEU":

        msg = fonte.render(
            "ESCAPOU COM SUCESSO! Pressione R para jogar.",
            True,
            VERDE_HEROI
        )

        tela.blit(msg, (100, ALTURA // 2))

    pygame.display.flip()
    relogio.tick(60)