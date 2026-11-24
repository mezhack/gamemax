
import pygame
import sys

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

guarda = pygame.Rect(380, 250, 40, 40)
velocidade_guarda = 4
direcao_guarda = 1

chave = pygame.Rect(700, 80, 20, 20)
porta = pygame.Rect(720, 500, 45, 65)


obstaculos = [
    pygame.Rect(180, 150, 35, 300),
    pygame.Rect(360, 40, 35, 170),
    pygame.Rect(540, 350, 160, 35)
]

# Estados do Jogo
pegou_chave = False
status_jogo = "JOGANDO"

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Reiniciar com a tecla R
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            heroi.topleft = (60, 60)
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

    
        heroi.x += dx
        heroi.x = max(0, min(LARGURA - heroi.width, heroi.x))

        for parede in obstaculos:
            if heroi.colliderect(parede):
                if dx > 0:
                    heroi.right = parede.left
                elif dx < 0:
                    heroi.left = parede.right

        
        heroi.y += dy
        heroi.y = max(0, min(ALTURA - heroi.height, heroi.y))

        for parede in obstaculos:
            if heroi.colliderect(parede):
                if dy > 0:
                    heroi.bottom = parede.top
                elif dy < 0:
                    heroi.top = parede.bottom

        # Patrulha vertical do Guarda
        guarda.y += velocidade_guarda * direcao_guarda

        if guarda.top <= 40 or guarda.bottom >= ALTURA - 40:
            direcao_guarda *= -1

        # Colisões
        if not pegou_chave and heroi.colliderect(chave):
            pegou_chave = True

        if heroi.colliderect(guarda):
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

    # Desenha Herói e Guarda
    pygame.draw.rect(tela, VERDE_HEROI, heroi)
    pygame.draw.rect(tela, VERMELHO_GUARDA, guarda)

    # HUD / Interface
    texto_chave = "Chave: OK!" if pegou_chave else "Chave: Pendente"
    hud = fonte.render(texto_chave, True, BRANCO)
    tela.blit(hud, (20, 15))

    if status_jogo == "PERDEU":
        msg = fonte.render(
            "CAPTURADO! Pressione R para tentar novamente.",
            True, VERMELHO_GUARDA
        )
        tela.blit(msg, (140, ALTURA // 2))

    elif status_jogo == "VENCEU":
        msg = fonte.render(
            "ESCAPOU COM SUCESSO! Pressione R para jogar.",
            True, VERDE_HEROI
        )
        tela.blit(msg, (140, ALTURA // 2))

    pygame.display.flip()

    relogio.tick(60)
