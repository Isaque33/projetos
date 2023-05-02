import pygame
from pygame.locals import *
from sys import exit
import os
from random import randrange, choice

pygame.init()
pygame.mixer.init()  # Inicia o mixer

diretório_principal = os.path.dirname(__file__)  # Pega o caminho do diretório Aulas 14-21 - Dino Game
diretório_imagens = os.path.join(diretório_principal, 'Imagens')  # coloca o caminho da pasta Imagens na variável diretório_imagens
diretório_sons = os.path.join(diretório_principal, 'Sons')  # coloca o caminho da pasta Sonss na variável diretório_sons

LARGURA = 640
ALTURA = 480

BRANCO = (255, 255, 255)

tela = pygame.display.set_mode((LARGURA, ALTURA))

pygame.display.set_caption('Dino Game')

sprite_sheet = pygame.image.load(os.path.join(diretório_imagens, 'dinoSpritesheet.png')).convert_alpha(tela)
# Se a imagem possuir transparência, conserva a transparência, ignorando o fundo da imagem(convert.aplha)

som_colisão = pygame.mixer.Sound(os.path.join(diretório_sons, 'death_sound.wav'))
som_colisão.set_volume(1)

som_pontuação = pygame.mixer.Sound(os.path.join(diretório_sons, 'score_sound.wav'))
som_pontuação.set_volume(1)

colidiu = False

escolha_obstáculo = choice([0, 1])

pontos = 0

velocidade_jogo = 10

def exibe_mensagem(msg, tamanho, cor):
    fonte = pygame.font.SysFont('comicsansms', tamanho, True, False)
    mensagem = f'{msg}'
    texto_formatado = fonte.render(mensagem, True, cor)
    return texto_formatado


def reiniciar_jogo():
    global pontos, velocidade_jogo, colidiu, escolha_obstáculo
    pontos = 0
    velocidade_jogo = 10
    colidiu = False
    dino_voador.rect.x = LARGURA
    cacto.rect.x = LARGURA
    escolha_obstáculo = choice([0, 1])
    dino.rect.y = dino.pos_y_inicial
    dino.pulo = False


class Dino(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.som_pulo = pygame.mixer.Sound(os.path.join(diretório_sons, 'jump_sound.wav'))
        self.som_pulo.set_volume(1)
        self.imagens_dinossauro = []
        c = 0
        for i in range(3):
            # Recortando os 3 primeiros frames da sprite sheet
            img = sprite_sheet.subsurface((i*32,0), (32, 32))  # Guarda a imagem do frame i da sprite sheet na variável img
            img = pygame.transform.scale(img, (32*3, 32*3))
            self.imagens_dinossauro.append(img)

        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)  # Cria a máscara do dinossauro
        self.pos_y_inicial = ALTURA - 64 - 96//2  # Posiciona o dinossauro sobre o chão, pois 64 é o tamanho do chão e 96//2 é o canto superior esquerdo do dino
        self.rect.center = (100, ALTURA - 64)
        self.pulo = False

    def pular(self):
        self.pulo = True
        self.som_pulo.play()

    def update(self):
        if self.pulo == True:
            if self.rect.y <= 200:
                self.pulo = False
            self.rect.y -= 20
        else:
            if self.rect.y < self.pos_y_inicial:
                self.rect.y += 15
            else:
                self.rect.y = self.pos_y_inicial

        if self.index_lista > 2:
            self.index_lista = 0
        self.index_lista += 0.25
        self.image = self.imagens_dinossauro[int(self.index_lista)]


class Nuvens(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((7*32,0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32*3, 32*3))
        self.rect = self.image.get_rect()
        self.rect.y = randrange(50, 200, 50)
        self.rect.x = LARGURA - randrange(30, 300, 90)

    def update(self):
        if self.rect.topright[0] < 0:  # Se a posição x do topo direito do retângulo da núvem sumir da tela:
            self.rect.x = LARGURA
            self.rect.y = randrange(50, 200, 50)  # Move a nuvem para a esquerda
        self.rect.x -= velocidade_jogo


class Chão(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((6*32,0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32*2, 32*2))
        self.rect = self.image.get_rect()
        self.rect.y = ALTURA - 64
        self.rect.x = pos_x * 64 # Posição x da sprite é a posição passada como parametro * 64(tamanho do chão)

    def update(self):
        if self.rect.topright[0] < 0:  # Se a posição x do topo direito do retângulo do chão sumir da tela:
            self.rect.x = LARGURA
        self.rect.x -= 10  # Move o chão para a esquerda


class Cacto(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((5*32,0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32*2, 32*2))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)  # Cria a máscara do cacto
        self.escolha = escolha_obstáculo
        self.rect.center = (LARGURA, ALTURA - 64)
        self.rect.x = LARGURA

    def update(self):
        if self.escolha == 0:
            if self.rect.topright[0] < 0:
                self.rect.x = LARGURA
            self.rect.x -= velocidade_jogo


class DinoVoador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.imagens_dinossauro = []
        for i in range(3, 5):
            img = sprite_sheet.subsurface((i*32, 0), (32, 32))
            img = pygame.transform.scale(img, (32*3, 32*3))
            self.imagens_dinossauro.append(img)

        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.mask = pygame.mask.from_surface(self.image)
        self.escolha = escolha_obstáculo
        self.rect = self.image.get_rect()
        self.rect.center = (LARGURA, 300)
        self.rect.x = LARGURA

    def update(self):
        if self.escolha == 1:
            if self.rect.topright[0] < 0:
                self.rect.x = LARGURA
            self.rect.x -= velocidade_jogo

            if self.index_lista > 1:
                self.index_lista = 0
            self.index_lista += 0.25
            self.image = self.imagens_dinossauro[int(self.index_lista)]

todas_as_sprites = pygame.sprite.Group()
dino = Dino()
todas_as_sprites.add(dino)

for i in range(4):
    nuvem = Nuvens()
    todas_as_sprites.add(nuvem)

for i in range(LARGURA//64+8):  # Criando 18 chãos
    chão = Chão(i)  # Cria a instancia chão passando como parametro i, que vai ser multiplicado por 64
    todas_as_sprites.add(chão)

cacto = Cacto()
todas_as_sprites.add(cacto)

dino_voador = DinoVoador()
todas_as_sprites.add(dino_voador)

grupo_obstáculos = pygame.sprite.Group()
grupo_obstáculos.add(cacto)
grupo_obstáculos.add(dino_voador)

relógio = pygame.time.Clock()
while True:
    relógio.tick(30)
    tela.fill(BRANCO)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                if dino.rect.y != dino.pos_y_inicial:
                    pass
                elif colidiu == True:
                    som_colisão.play()
                else:
                    dino.pular()
            if event.key == K_r and colidiu == True:
                reiniciar_jogo()

    colisões = pygame.sprite.spritecollide(dino, grupo_obstáculos, False, pygame.sprite.collide_mask)  # Guarda o comando da colisão entre 2 sprites
    
    todas_as_sprites.draw(tela)

    if cacto.rect.topright[0] <= 0 or dino_voador.rect.topright[0] <= 0:
        escolha_obstáculo = choice([0, 1])
        cacto.rect.x = LARGURA
        dino_voador.rect.x = LARGURA
        cacto.escolha = escolha_obstáculo
        dino_voador.escolha = escolha_obstáculo

    if colisões and colidiu == False:
        som_colisão.play()
        colidiu = True

    if colidiu == True:
        game_over = exibe_mensagem('GAME OVER', 40, (0, 0, 0))
        tela.blit(game_over, (LARGURA//2, ALTURA//2))
        restart = exibe_mensagem('Pressione R para reiniciar', 20, (0, 0, 0))
        tela.blit(restart, (LARGURA//2, (ALTURA//2) + 60))
    else:
        pontos += 1
        todas_as_sprites.update()
        texto_pontos = exibe_mensagem(pontos, 40, (0, 0, 0))

    if pontos % 100 == 0 and colidiu == False:
        som_pontuação.play()
        if velocidade_jogo >= 23:
            velocidade_jogo = 23
        else:
            velocidade_jogo += 1

    tela.blit(texto_pontos, (520, 30))
    
    pygame.display.flip()