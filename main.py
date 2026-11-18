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

#guarda = pygame.Rect(380, 400, 40, 40)
# Configuração do Guarda e Rota
rota_guarda = [(180, 460), (620, 460), (620, 60), (180, 60)]
ponto_atual = 0

guarda = pygame.Rect(0, 0, 40, 40)
guarda.center = rota_guarda[0]  # Nasce na parte de baixo à esquerda
velocidade_guarda = 4


chave = pygame.Rect(400, 340, 20, 20)
porta = pygame.Rect(735, 20, 45, 65)

#(Missão do Aluno): Adicione aqui uma lista de paredes/obstáculos!
obstaculos = [pygame.Rect(250, 250, 300, 30),
pygame.Rect(250, 250, 30,150 ),
pygame.Rect(530, 250, 30, 150),
pygame.Rect(710, 0, 10, 150),
pygame.Rect(790, 0, 10, 150),
pygame.Rect(710, 0, 100, 10)]

# Estados do Jogo
pegou_chave = False
status_jogo = "JOGANDO"  # Pode ser: "JOGANDO", "VENCEU", "PERDEU"

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Reiniciar com a tecla R
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            heroi.topleft = (60, 60)
            ponto_atual = 0
            guarda.center = rota_guarda[0]
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

        # Atualiza posição mantendo dentro da tela
                # 1. Move no eixo X e checa colisão com as paredes
        heroi.x = max(0, min(LARGURA - heroi.width, heroi.x + dx))
        for parede in obstaculos:
            if heroi.colliderect(parede):
                if dx > 0:  # Estava indo para a direita
                    heroi.right = parede.left
                elif dx < 0:  # Estava indo para a esquerda
                    heroi.left = parede.right

        # 2. Move no eixo Y e checa colisão com as paredes
        heroi.y = max(0, min(ALTURA - heroi.height, heroi.y + dy))
        for parede in obstaculos:
            if heroi.colliderect(parede):
                if dy > 0:  # Estava descendo
                    heroi.bottom = parede.top
                elif dy < 0:  # Estava subindo
                    heroi.top = parede.bottom


        # Patrulha vertical do Guarda
                # Patrulha vertical do Guarda
                # Patrulha ao redor do mapa (Waypoints)
        alvo_x, alvo_y = rota_guarda[ponto_atual]
        dx_g = alvo_x - guarda.centerx
        dy_g = alvo_y - guarda.centery
        distancia = math.hypot(dx_g, dy_g)

        if distancia <= velocidade_guarda:
            guarda.center = (alvo_x, alvo_y)
            ponto_atual = (ponto_atual + 1) % len(rota_guarda)  # Vai para o próximo ponto em loop
        else:
            guarda.x += round((dx_g / distancia) * velocidade_guarda)
            guarda.y += round((dy_g / distancia) * velocidade_guarda)


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

    # Desenha Obstáculos (quando implementados)
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
        msg = fonte.render("CAPTURADO! Pressione R para tentar novamente.", True, VERMELHO_GUARDA)
        tela.blit(msg, (140, ALTURA // 2))
    elif status_jogo == "VENCEU":
        msg = fonte.render("ESCAPOU COM SUCESSO! Pressione R para jogar.", True, VERDE_HEROI)
        tela.blit(msg, (140, ALTURA // 2))

    pygame.display.flip()
    relogio.tick(60)