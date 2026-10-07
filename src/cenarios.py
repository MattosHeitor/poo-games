import math
import random

import pygame

from vampiro import Vampiro
from chefe_final import ChefeFinal
from inimigos_novos import Esqueleto, Bruxa, AranhaGigante, Golem

LARGURA = 960
ALTURA = 400
CHAO = 300          # linha onde o céu termina e o chão começa

# Partículas de ambiente de cada cenário: (cor, velocidade de subida)
# None = cenário sem partículas
AMBIENTE = {
    "floresta": ((220, 255, 120), 15),     # vaga-lumes
    "montanhas": None,
    "vulcao": ((255, 150, 50), 60),        # brasas
    "noite": ((200, 200, 255), 8),         # poeira brilhante
    "trevas": ((190, 100, 255), 35),       # energia sombria
    "pantano": ((140, 255, 120), 12),      # luzes do pântano
    "caverna": ((150, 220, 255), 10),      # brilho dos cristais
    "ruinas": ((255, 230, 160), 20),       # poeira dourada
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def misturar(cor_a, cor_b, t):
    """Mistura duas cores. t = 0 dá cor_a, t = 1 dá cor_b."""
    return tuple(int(a + (b - a) * t) for a, b in zip(cor_a, cor_b))


def criar_degrade(largura, altura, cor_topo, cor_baixo):
    """Surface com degradê vertical (uma linha de cada cor)."""
    imagem = pygame.Surface((largura, altura))
    for y in range(altura):
        cor = misturar(cor_topo, cor_baixo, y / (altura - 1))
        pygame.draw.line(imagem, cor, (0, y), (largura, y))
    return imagem


def astro(tela, cor, centro, raio):
    """Sol ou lua com brilho em volta."""
    for i in range(4, 0, -1):
        tamanho = int(raio * 2 * (1 + i * 0.4))
        camada = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        r = camada.get_width() // 2
        pygame.draw.circle(camada, (*cor, 25), (r, r), r)
        tela.blit(camada, (centro[0] - r, centro[1] - r))
    pygame.draw.circle(tela, cor, centro, raio)


def montanhas(tela, cor, altura_base, variacao, passo, sorteio, neve=None):
    """Linha de montanhas pontudas até o chão."""
    pontos = [(0, CHAO)]
    x = -passo // 2
    while x < LARGURA + passo:
        pontos.append((x, altura_base - sorteio.uniform(0, variacao)))
        pontos.append((x + passo // 2, altura_base + sorteio.uniform(10, 40)))
        x += passo
    pontos.append((LARGURA, CHAO))
    pygame.draw.polygon(tela, cor, pontos)

    if neve:
        # Pico com neve: pequeno triângulo no topo de cada montanha
        for i in range(1, len(pontos) - 2, 2):
            px, py = pontos[i]
            pygame.draw.polygon(tela, neve, [(px, py), (px - 16, py + 22), (px + 16, py + 22)])


def chao(tela, cor, cor_borda):
    pygame.draw.rect(tela, cor, (0, CHAO, LARGURA, ALTURA - CHAO))
    pygame.draw.rect(tela, cor_borda, (0, CHAO, LARGURA, 10))


def tufos_de_grama(tela, cor, sorteio):
    for _ in range(60):
        x = sorteio.uniform(0, LARGURA)
        y = sorteio.uniform(CHAO + 15, ALTURA)
        pygame.draw.polygon(tela, cor, [(x - 4, y), (x + 4, y), (x, y - 9)])


# ============================================================
# ESCOLHA DO CENÁRIO
# ============================================================

def tipo_de_cenario(inimigo):
    if isinstance(inimigo, ChefeFinal):
        return "trevas"
    if isinstance(inimigo, (Vampiro, Esqueleto)):
        return "noite"
    if isinstance(inimigo, Bruxa):
        return "pantano"
    if isinstance(inimigo, AranhaGigante):
        return "caverna"
    if isinstance(inimigo, Golem):
        return "ruinas"
    if inimigo.nome == "Orc":
        return "montanhas"
    if inimigo.nome == "Dragão Jovem":
        return "vulcao"
    return "floresta"


def criar_cenario(tipo):
    # Sorteio com semente fixa: o cenário sai sempre igual
    sorteio = random.Random(7)

    if tipo == "montanhas":
        return cenario_montanhas(sorteio)
    if tipo == "vulcao":
        return cenario_vulcao(sorteio)
    if tipo == "noite":
        return cenario_noite(sorteio)
    if tipo == "trevas":
        return cenario_trevas(sorteio)
    if tipo == "pantano":
        return cenario_pantano(sorteio)
    if tipo == "caverna":
        return cenario_caverna(sorteio)
    if tipo == "ruinas":
        return cenario_ruinas(sorteio)
    return cenario_floresta(sorteio)


# ============================================================
# CENÁRIOS
# ============================================================

def cenario_floresta(sorteio):
    tela = criar_degrade(LARGURA, ALTURA, (85, 55, 135), (255, 175, 105))
    astro(tela, (255, 225, 150), (480, 250), 60)

    montanhas(tela, (150, 90, 130), 230, 50, 220, sorteio)

    # Pinheiros em silhueta
    for x in range(-20, LARGURA + 40, 48):
        altura = sorteio.uniform(90, 150)
        cor = (60, 45, 90)
        for andar in range(3):
            topo = CHAO - altura + andar * altura * 0.25
            largura = 22 + andar * 10
            pygame.draw.polygon(tela, cor, [(x, topo), (x - largura, topo + altura * 0.45),
                                            (x + largura, topo + altura * 0.45)])

    chao(tela, (70, 125, 65), (100, 160, 80))
    tufos_de_grama(tela, (55, 100, 50), sorteio)
    return tela


def cenario_montanhas(sorteio):
    tela = criar_degrade(LARGURA, ALTURA, (95, 155, 235), (245, 215, 175))
    astro(tela, (255, 250, 225), (820, 80), 34)

    # Nuvens
    for _ in range(5):
        x = sorteio.uniform(0, LARGURA)
        y = sorteio.uniform(40, 140)
        for dx in (-30, 0, 30):
            pygame.draw.ellipse(tela, (255, 255, 255), (x + dx, y - abs(dx) * 0.3, 70, 30))

    montanhas(tela, (140, 150, 190), 150, 60, 200, sorteio, neve=(245, 245, 255))
    montanhas(tela, (95, 115, 130), 230, 40, 160, sorteio)

    chao(tela, (130, 115, 70), (110, 150, 70))
    tufos_de_grama(tela, (100, 130, 60), sorteio)
    return tela


def cenario_vulcao(sorteio):
    tela = criar_degrade(LARGURA, ALTURA, (35, 8, 15), (205, 75, 30))

    # Vulcão com lava escorrendo
    pygame.draw.polygon(tela, (65, 28, 28), [(260, CHAO), (450, 90), (530, 95), (720, CHAO)])
    astro(tela, (255, 140, 40), (490, 95), 32)
    pygame.draw.polygon(tela, (65, 28, 28), [(440, 105), (540, 105), (530, 95), (450, 90)])
    pygame.draw.polygon(tela, (255, 120, 30), [(480, 100), (500, 100), (530, 200), (515, CHAO), (495, CHAO), (505, 200)])
    pygame.draw.polygon(tela, (255, 210, 90), [(486, 100), (494, 100), (515, 200), (507, CHAO), (501, CHAO), (508, 200)])

    # Fumaça
    for i in range(6):
        pygame.draw.ellipse(tela, (60, 40, 45), (430 + i * 18, 60 - i * 12, 90, 40))

    montanhas(tela, (50, 22, 25), 250, 40, 180, sorteio)

    # Chão de pedra com rachaduras de lava
    chao(tela, (55, 35, 35), (80, 45, 40))
    for _ in range(14):
        x = sorteio.uniform(0, LARGURA)
        y = sorteio.uniform(CHAO + 20, ALTURA - 10)
        pontos = [(x, y)]
        for _ in range(3):
            x += sorteio.uniform(15, 35)
            y += sorteio.uniform(-8, 8)
            pontos.append((x, y))
        pygame.draw.lines(tela, (255, 130, 40), False, pontos, 3)
    return tela


def cenario_noite(sorteio):
    tela = criar_degrade(LARGURA, ALTURA, (8, 8, 30), (60, 40, 100))

    # Estrelas
    for _ in range(90):
        x = sorteio.uniform(0, LARGURA)
        y = sorteio.uniform(0, 230)
        pygame.draw.circle(tela, (230, 230, 255), (int(x), int(y)), sorteio.choice((1, 1, 2)))

    # Lua com crateras
    astro(tela, (240, 240, 215), (760, 95), 46)
    for cx, cy, r in ((745, 85, 9), (775, 110, 6), (770, 78, 4)):
        pygame.draw.circle(tela, (215, 215, 190), (cx, cy), r)

    montanhas(tela, (35, 30, 65), 240, 50, 200, sorteio)

    # Árvores secas
    for x in (90, 380, 870):
        pygame.draw.line(tela, (25, 20, 40), (x, CHAO), (x, CHAO - 120), 8)
        pygame.draw.line(tela, (25, 20, 40), (x, CHAO - 80), (x - 35, CHAO - 120), 5)
        pygame.draw.line(tela, (25, 20, 40), (x, CHAO - 100), (x + 30, CHAO - 140), 5)

    chao(tela, (40, 48, 58), (55, 65, 78))

    # Lápides
    for x in (60, 330, 470, 900):
        pygame.draw.rect(tela, (85, 85, 100), (x, CHAO + 8, 26, 34), border_top_left_radius=13, border_top_right_radius=13)
        pygame.draw.line(tela, (55, 55, 70), (x + 13, CHAO + 16), (x + 13, CHAO + 30), 3)
        pygame.draw.line(tela, (55, 55, 70), (x + 7, CHAO + 21), (x + 19, CHAO + 21), 3)
    return tela


def cenario_trevas(sorteio):
    tela = criar_degrade(LARGURA, ALTURA, (12, 0, 22), (115, 20, 60))
    astro(tela, (220, 70, 70), (480, 120), 58)

    # Castelo em silhueta com janelas acesas
    cor = (22, 8, 32)
    pygame.draw.rect(tela, cor, (300, 150, 360, CHAO - 150))
    for x, largura, altura in ((280, 50, 210), (390, 40, 240), (530, 40, 240), (630, 50, 210)):
        topo = CHAO - altura
        pygame.draw.rect(tela, cor, (x, topo, largura, altura))
        pygame.draw.polygon(tela, cor, [(x - 6, topo), (x + largura + 6, topo), (x + largura // 2, topo - 45)])
        pygame.draw.rect(tela, (255, 170, 60), (x + largura // 2 - 4, topo + 30, 8, 14))
    for x in range(310, 660, 28):
        pygame.draw.rect(tela, cor, (x, 138, 16, 14))

    montanhas(tela, (30, 10, 40), 260, 30, 160, sorteio)

    # Chão com rachaduras roxas
    chao(tela, (40, 22, 50), (60, 30, 75))
    for _ in range(12):
        x = sorteio.uniform(0, LARGURA)
        y = sorteio.uniform(CHAO + 20, ALTURA - 10)
        pontos = [(x, y)]
        for _ in range(3):
            x += sorteio.uniform(15, 35)
            y += sorteio.uniform(-8, 8)
            pontos.append((x, y))
        pygame.draw.lines(tela, (160, 70, 230), False, pontos, 2)
    return tela


def cenario_pantano(sorteio):
    tela = criar_degrade(LARGURA, ALTURA, (25, 40, 35), (110, 140, 90))
    astro(tela, (220, 235, 190), (180, 90), 30)

    # Árvores tortas com galhos pendurados
    for x in (60, 250, 700, 880):
        cor = (35, 45, 35)
        pygame.draw.polygon(tela, cor, [(x - 14, CHAO), (x + 14, CHAO), (x + 8, CHAO - 150), (x - 6, CHAO - 150)])
        pygame.draw.ellipse(tela, cor, (x - 70, CHAO - 210, 140, 80))
        for dx in (-50, -20, 15, 45):
            pygame.draw.line(tela, (60, 80, 50), (x + dx, CHAO - 150), (x + dx + 3, CHAO - 100), 2)

    montanhas(tela, (55, 75, 55), 250, 30, 200, sorteio)

    # Chão lamacento com poças
    chao(tela, (60, 70, 45), (80, 95, 55))
    for x in (120, 420, 620, 840):
        pygame.draw.ellipse(tela, (70, 110, 90), (x, CHAO + 30, 110, 22))
        pygame.draw.ellipse(tela, (110, 160, 130), (x + 20, CHAO + 34, 40, 6))
    tufos_de_grama(tela, (70, 100, 50), sorteio)
    return tela


def cenario_caverna(sorteio):
    tela = criar_degrade(LARGURA, ALTURA, (15, 12, 25), (55, 45, 70))

    # Estalactites no teto
    for x in range(0, LARGURA, 40):
        altura = sorteio.uniform(30, 90)
        pygame.draw.polygon(tela, (35, 28, 45), [(x, 0), (x + 40, 0), (x + 20, altura)])

    # Teias nos cantos
    for cx, cy in ((0, 0), (LARGURA, 0)):
        for r in (60, 110, 160):
            pygame.draw.circle(tela, (120, 115, 140), (cx, cy), r, 1)
        for i in range(6):
            angulo = i * 0.3 + (0 if cx == 0 else 1.6)
            fim = (cx + math.cos(angulo) * 170, cy + math.sin(angulo) * 170)
            pygame.draw.line(tela, (120, 115, 140), (cx, cy), fim, 1)

    # Cristais brilhantes nas paredes
    for x, y in ((150, 230), (420, 260), (600, 220), (830, 250)):
        astro(tela, (110, 200, 255), (x, y), 4)
        pygame.draw.polygon(tela, (120, 210, 255), [(x - 10, y + 30), (x, y - 20), (x + 10, y + 30)])

    chao(tela, (45, 38, 55), (65, 55, 78))
    for _ in range(25):
        x = sorteio.uniform(0, LARGURA)
        y = sorteio.uniform(CHAO + 20, ALTURA - 5)
        pygame.draw.ellipse(tela, (70, 62, 85), (x, y, 18, 9))
    return tela


def cenario_ruinas(sorteio):
    tela = criar_degrade(LARGURA, ALTURA, (240, 160, 90), (250, 215, 160))
    astro(tela, (255, 240, 200), (480, 210), 70)

    montanhas(tela, (190, 140, 110), 220, 50, 220, sorteio)

    # Colunas quebradas
    for x, altura in ((90, 170), (230, 120), (720, 150), (860, 190)):
        cor = (215, 195, 165)
        pygame.draw.rect(tela, cor, (x, CHAO - altura, 40, altura))
        pygame.draw.rect(tela, (185, 165, 140), (x - 6, CHAO - altura - 10, 52, 12))
        for dx in (10, 20, 30):
            pygame.draw.line(tela, (190, 170, 145), (x + dx, CHAO - altura), (x + dx, CHAO), 2)
        pygame.draw.polygon(tela, (240, 160, 90) if altura < 160 else (250, 200, 140),
                            [(x, CHAO - altura - 10), (x + 25, CHAO - altura - 10), (x + 10, CHAO - altura + 15)])

    chao(tela, (175, 140, 95), (200, 165, 115))
    for _ in range(18):
        x = sorteio.uniform(0, LARGURA)
        y = sorteio.uniform(CHAO + 20, ALTURA - 10)
        pygame.draw.rect(tela, (150, 120, 85), (x, y, sorteio.uniform(10, 26), 8), border_radius=3)
    return tela
