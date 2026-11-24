
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

# Personagens e objetos
heroi = pygame.Rect(60, 60, 35, 35)
velocidade_heroi = 5

guarda = pygame.Rect(380, 250, 40, 40)
velocidade_guarda = 4
direcao_guarda = 1

chave = pygame.Rect(700, 80, 20, 20)
porta = pygame.Rect(720, 500, 45, 65)

# Três paredes adicionadas
obstaculos = [
    pygame.Rect(180, 120, 250, 25),
    pygame.Rect(100, 300, 25, 180),
    pygame.Rect(480, 380, 200, 25)
]

# Estados do jogo
pegou_chave = False
status_jogo = "JOGANDO"


def mover_com_colisao(personagem, dx, dy):
    # Movimento horizontal
    personagem.x += dx

    for parede in obstaculos:
        if personagem.colliderect(parede):
            if dx > 0:
                personagem.right = parede.left
            elif dx < 0:
                personagem.left = parede.right

    # Movimento vertical
    personagem.y += dy

    for parede in obstaculos:
        if personagem.colliderect(parede):
            if dy > 0:
                personagem.bottom = parede.top
            elif dy < 0:
                personagem.top = parede.bottom

    # Impede sair da tela
    personagem.clamp_ip(tela.get_rect())


while True:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Reiniciar o jogo
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            heroi.topleft = (60, 60)
            guarda.topleft = (380, 250)
            direcao_guarda = 1
            pegou_chave = False
            status_jogo = "JOGANDO"

    if status_jogo == "JOGANDO":

        # Movimentação do herói
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

        mover_com_colisao(heroi, dx, dy)

        # Patrulha do guarda
        guarda.y += velocidade_guarda * direcao_guarda

        if guarda.top <= 40 or guarda.bottom >= ALTURA - 40:
            direcao_guarda *= -1

        # Colisão com a chave
        if not pegou_chave and heroi.colliderect(chave):
            pegou_chave = True

        # Colisão com o guarda
        if heroi.colliderect(guarda):
            status_jogo = "PERDEU"

        # Verifica se chegou na porta
        if pegou_chave and heroi.colliderect(porta):
            status_jogo = "VENCEU"

    # Desenho da tela
    tela.fill(PRETO)

    # Porta
    pygame.draw.rect(tela, AZUL_PORTA, porta)

    # Chave
    if not pegou_chave:
        pygame.draw.rect(tela, AMARELO_CHAVE, chave)

    # Paredes
    for parede in obstaculos:
        pygame.draw.rect(tela, CINZA_PAREDE, parede)

    # Personagens
    pygame.draw.rect(tela, VERDE_HEROI, heroi)
    pygame.draw.rect(tela, VERMELHO_GUARDA, guarda)

    # Interface
    texto_chave = "Chave: OK!" if pegou_chave else "Chave: Pendente"
    hud = fonte.render(texto_chave, True, BRANCO)
    tela.blit(hud, (20, 15))

    if status_jogo == "PERDEU":
        msg = fonte.render(
            "CAPTURADO! Pressione R para tentar novamente.",
            True, VERMELHO_GUARDA
        )
        tela.blit(msg, (100, ALTURA // 2))

    elif status_jogo == "VENCEU":
        msg = fonte.render(
            "ESCAPOU COM SUCESSO! Pressione R para jogar.",
            True, VERDE_HEROI
        )
        tela.blit(msg, (100, ALTURA // 2))

    pygame.display.flip()
    relogio.tick(60)
