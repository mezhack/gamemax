import pygame,random
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
CINZA_PAREDE = (32, 124, 72)
BRANCO = (255, 255, 255)

# Entidades do Jogo
heroi = pygame.Rect(60, 60, 35, 35)
velocidade_heroi = 5
guarda_preso=False
guarda_preso_2=False

guarda = pygame.Rect(380, 250, 40, 40)
velocidade_guarda = 4
direcao_guarda = 1  # 1 = desce, -1 = sobe

guarda_2 = pygame.Rect(402, 200, 18, 18)
velocidade_guarda_2 = 10
direcao_guarda_2 = -1

chave = pygame.Rect(700, 80, 20, 20)
porta = pygame.Rect(720, 500, 45, 65)

# TODO (Missão do Aluno): Adicione aqui uma lista de paredes/obstáculos!
obstaculos = [(400, 80, 200, 20),(200, 40, 20, 200),(5, 10, 42, 21)]

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
            pegou_chave = False
            status_jogo = "JOGANDO"

    if status_jogo == "JOGANDO":
        pah_x,pah_y=heroi.x,heroi.y
        #posição_anterior_heroi
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
        heroi.x = max(0, min(LARGURA - heroi.width, heroi.x + dx))
        heroi.y = max(0, min(ALTURA - heroi.height, heroi.y + dy))
        for paredes in obstaculos:
            if heroi.colliderect(paredes):
                print("colidiu")
                heroi.x, heroi.y = pah_x, pah_y

        # Patrulha vertical do Guarda
        #posição_anterior_guarda

        pag_x,pag_y=guarda.x,guarda.y
        if guarda_preso == True:
            guarda.x+=(velocidade_guarda*random.randint(-1,1))
            guarda.y+=(velocidade_guarda*random.randint(-1,1))
            guarda_preso=False
        guarda.y += velocidade_guarda * direcao_guarda
        for paredes in obstaculos:
            if guarda.colliderect(paredes):
                guarda.x,guarda.y = pag_x,pag_y
                guarda_preso=True
        if guarda.top <= 40 or guarda.bottom >= ALTURA - 40:
            direcao_guarda *= -1

        pag2_x,pag2_y = guarda_2.x,guarda_2.y
        if guarda_preso_2 == True:
            guarda_2.x+=(velocidade_guarda_2*random.randint(-1,1))
            guarda_2.y+=(velocidade_guarda_2*random.randint(-1,1))
            guarda_preso_2=False
        guarda_2.x += velocidade_guarda_2 * direcao_guarda_2
        for paredes in obstaculos:
            if guarda_2.colliderect(paredes):
                guarda_2.x,guarda_2.y = pag2_x,pag2_y
                print("colidiy")
                guarda_preso_2=True
        if guarda_2.left <= 18 or guarda_2.right >= LARGURA - 18:
            direcao_guarda_2 *= -1

        # Colisões
        if not pegou_chave and heroi.colliderect(chave):
            pegou_chave = True

        if heroi.colliderect(guarda)or heroi.colliderect(guarda_2):
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
    pygame.draw.rect(tela, VERMELHO_GUARDA, guarda_2)

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