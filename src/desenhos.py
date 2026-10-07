import math

import pygame

from guerreiro import Guerreiro
from barbaro import Barbaro
from paladino import Paladino
from assassina import Assassina
from mago import Mago
from arqueiro import Arqueiro
from vampiro import Vampiro
from chefe_final import ChefeFinal
from inimigos_novos import Esqueleto, Bruxa, AranhaGigante, Golem

# Cada desenho é pensado numa "folha" de 160 x 200 pixels, com o
# personagem virado para a DIREITA e os pés em y = 190.
#
# Para os desenhos ficarem mais lisos, desenhamos tudo 3 vezes maior
# (SUPER = 3) e depois diminuímos a imagem.
#
# Cada personagem tem QUADROS desenhos um pouco diferentes (capa
# balançando, chamas, brilhos). Trocando os quadros rápido, o
# personagem parece estar sempre se mexendo.
LARGURA_DESENHO = 160
ALTURA_DESENHO = 200
SUPER = 3
QUADROS = 8

CONTORNO = (25, 20, 35)
ESPESSURA = 4

PELE = (245, 205, 165)
BRANCO = (245, 245, 250)
OURO = (240, 195, 60)
COURO = (125, 80, 45)
OSSO = (235, 228, 205)

# Guarda os desenhos já prontos para não redesenhar a cada quadro
_cache = {}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def ponto(p):
    return (round(p[0] * SUPER), round(p[1] * SUPER))


def escurecer(cor, fator=0.7):
    return tuple(int(c * fator) for c in cor[:3])


def clarear(cor, fator=0.35):
    return tuple(int(c + (255 - c) * fator) for c in cor[:3])


def poligono(folha, cor, pontos, contorno=True):
    pontos = [ponto(p) for p in pontos]
    pygame.draw.polygon(folha, cor, pontos)
    if contorno:
        pygame.draw.polygon(folha, CONTORNO, pontos, ESPESSURA)


def circulo(folha, cor, centro, raio, contorno=True):
    centro = ponto(centro)
    raio = max(1, round(raio * SUPER))
    pygame.draw.circle(folha, cor, centro, raio)
    if contorno:
        pygame.draw.circle(folha, CONTORNO, centro, raio, ESPESSURA)


def elipse(folha, cor, x, y, largura, altura, contorno=True):
    area = (x * SUPER, y * SUPER, largura * SUPER, altura * SUPER)
    pygame.draw.ellipse(folha, cor, area)
    if contorno:
        pygame.draw.ellipse(folha, CONTORNO, area, ESPESSURA)


def anel(folha, cor, x, y, largura, altura, espessura):
    area = (x * SUPER, y * SUPER, largura * SUPER, altura * SUPER)
    pygame.draw.ellipse(folha, cor, area, round(espessura * SUPER))


def retangulo(folha, cor, x, y, largura, altura, borda=0, contorno=True):
    area = (x * SUPER, y * SUPER, largura * SUPER, altura * SUPER)
    pygame.draw.rect(folha, cor, area, border_radius=borda * SUPER)
    if contorno:
        pygame.draw.rect(folha, CONTORNO, area, ESPESSURA, border_radius=borda * SUPER)


def linha(folha, cor, inicio, fim, largura, contorno=True):
    # Linha com pontas arredondadas (braços, cabos, ossos)
    inicio = ponto(inicio)
    fim = ponto(fim)
    largura = max(1, round(largura * SUPER))

    if contorno:
        grossa = largura + ESPESSURA * 2
        pygame.draw.line(folha, CONTORNO, inicio, fim, grossa)
        pygame.draw.circle(folha, CONTORNO, inicio, grossa // 2)
        pygame.draw.circle(folha, CONTORNO, fim, grossa // 2)

    pygame.draw.line(folha, cor, inicio, fim, largura)
    pygame.draw.circle(folha, cor, inicio, largura // 2)
    pygame.draw.circle(folha, cor, fim, largura // 2)


def arco(folha, cor, x, y, largura, altura, angulo_inicial, angulo_final, espessura):
    area = (x * SUPER, y * SUPER, largura * SUPER, altura * SUPER)
    pygame.draw.arc(folha, CONTORNO, area, angulo_inicial, angulo_final, round(espessura * SUPER) + ESPESSURA)
    pygame.draw.arc(folha, cor, area, angulo_inicial, angulo_final, round(espessura * SUPER))


def brilho(folha, cor, centro, raio, transparencia):
    # Círculo semitransparente (aura, luz). É desenhado numa camada
    # separada e depois colado, para se misturar com o que está embaixo.
    transparencia = max(0, min(255, int(transparencia)))
    raio = max(1, round(raio * SUPER))
    camada = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    pygame.draw.circle(camada, (*cor[:3], transparencia), (raio, raio), raio)
    x, y = ponto(centro)
    folha.blit(camada, (x - raio, y - raio))


def chama(folha, x, y, altura, largura, cores, a):
    """Chama em camadas (de fora para dentro) que balança com o quadro."""
    balanco = math.sin(a)
    tremor = math.sin(a * 2)

    for i, cor in enumerate(cores):
        escala = 1 - i * 0.3
        h = altura * escala * (1 + 0.12 * tremor)
        meia = largura * escala / 2
        pontos = [
            (x - meia, y),
            (x - meia * 0.9, y - h * 0.45),
            (x + balanco * meia * 0.5, y - h),
            (x + meia * 0.9, y - h * 0.5),
            (x + meia, y),
            (x, y + meia * 0.5),
        ]
        poligono(folha, cor, pontos, contorno=False)


def estrela(cx, cy, raio_externo, raio_interno, pontas=5):
    pontos = []
    for i in range(pontas * 2):
        raio = raio_externo if i % 2 == 0 else raio_interno
        angulo = -math.pi / 2 + i * math.pi / pontas
        pontos.append((cx + math.cos(angulo) * raio, cy + math.sin(angulo) * raio))
    return pontos


def folha_de_arvore(folha, cx, cy, angulo, comprimento, largura, cor):
    dx = math.cos(angulo) * comprimento / 2
    dy = math.sin(angulo) * comprimento / 2
    px = -math.sin(angulo) * largura / 2
    py = math.cos(angulo) * largura / 2
    poligono(folha, cor, [(cx - dx, cy - dy), (cx + px, cy + py), (cx + dx, cy + dy), (cx - px, cy - py)])


def runa(folha, x, y, tamanho, cor, intensidade):
    brilho(folha, cor, (x, y), tamanho * 1.8, 70 * intensidade)
    linha(folha, cor, (x, y - tamanho), (x, y + tamanho), 1, contorno=False)
    linha(folha, cor, (x - tamanho * 0.7, y - tamanho * 0.3), (x + tamanho * 0.7, y + tamanho * 0.3), 1, contorno=False)


# ============================================================
# ESCOLHA DO DESENHO
# ============================================================

def tipo_do_desenho(personagem):
    if isinstance(personagem, Barbaro):
        return "barbaro"
    if isinstance(personagem, Guerreiro):
        return "guerreiro"
    if isinstance(personagem, Paladino):
        return "paladino"
    if isinstance(personagem, Assassina):
        return "assassina"
    if isinstance(personagem, Mago):
        # Os magos elementais têm o atributo "elemento"
        return "mago" + getattr(personagem, "elemento", "")
    if isinstance(personagem, Arqueiro):
        return "arqueira"
    if isinstance(personagem, Esqueleto):
        return "esqueleto"
    if isinstance(personagem, Bruxa):
        return "bruxa"
    if isinstance(personagem, AranhaGigante):
        return "aranha"
    if isinstance(personagem, Golem):
        return "golem"
    if isinstance(personagem, Vampiro):
        return "vampiro"
    if isinstance(personagem, ChefeFinal):
        return "lich"
    if personagem.nome == "Goblin":
        return "goblin"
    if personagem.nome == "Orc":
        return "orc"
    if personagem.nome == "Dragão Jovem":
        return "dragao"
    return "generico"


def criar_desenho(personagem, extra=None, escala=1.0, quadro=0):
    """Devolve uma imagem (Surface) do personagem, virado para a direita.

    - extra: detalhe opcional (arma do bárbaro, golem carregando...).
    - escala: 1.0 = 160 x 200 pixels.
    - quadro: número do quadro da animação (0 até QUADROS - 1).
    """
    tipo = tipo_do_desenho(personagem)
    quadro = quadro % QUADROS
    chave = (tipo, extra, escala, quadro)

    if chave in _cache:
        return _cache[chave]

    folha = pygame.Surface((LARGURA_DESENHO * SUPER, ALTURA_DESENHO * SUPER), pygame.SRCALPHA)

    # Ângulo da animação: dá uma volta completa a cada QUADROS quadros
    a = 2 * math.pi * quadro / QUADROS

    if tipo == "guerreiro":
        desenhar_guerreiro(folha, a)
    elif tipo == "barbaro":
        desenhar_barbaro(folha, a, extra or "Machado")
    elif tipo == "paladino":
        desenhar_paladino(folha, a)
    elif tipo == "assassina":
        desenhar_assassina(folha, a)
    elif tipo.startswith("mago"):
        desenhar_mago(folha, a, tipo.replace("mago", ""))
    elif tipo == "arqueira":
        desenhar_arqueira(folha, a)
    elif tipo == "goblin":
        desenhar_goblin(folha, a)
    elif tipo == "esqueleto":
        desenhar_esqueleto(folha, a)
    elif tipo == "orc":
        desenhar_orc(folha, a)
    elif tipo == "bruxa":
        desenhar_bruxa(folha, a)
    elif tipo == "dragao":
        desenhar_dragao(folha, a)
    elif tipo == "vampiro":
        desenhar_vampiro(folha, a)
    elif tipo == "aranha":
        desenhar_aranha(folha, a)
    elif tipo == "golem":
        desenhar_golem(folha, a, extra == "carregando")
    elif tipo == "lich":
        desenhar_lich(folha, a)
    else:
        desenhar_generico(folha)

    tamanho = (int(LARGURA_DESENHO * escala), int(ALTURA_DESENHO * escala))
    imagem = pygame.transform.smoothscale(folha, tamanho)

    _cache[chave] = imagem
    return imagem


# ============================================================
# GUERREIRO: cavaleiro prateado e azul, elmo com asas
# ============================================================

def desenhar_guerreiro(folha, a):
    prata = (200, 205, 220)
    prata_escura = escurecer(prata, 0.72)
    azul = (40, 80, 175)
    azul_escuro = escurecer(azul, 0.6)
    bota = (70, 60, 85)
    s = math.sin(a)

    # Capa longa
    poligono(folha, azul_escuro, [(64, 82), (96, 82), (110 + s * 4, 188), (80, 183 + s * 2), (50 + s * 3, 188)])

    # Pernas com joelheiras e botas
    retangulo(folha, prata_escura, 68, 134, 12, 44, 4)
    retangulo(folha, prata, 81, 134, 12, 44, 4)
    circulo(folha, prata, (74, 153), 5)
    circulo(folha, prata, (87, 153), 5)
    retangulo(folha, bota, 64, 176, 17, 14, 4)
    retangulo(folha, bota, 79, 176, 18, 14, 4)

    # Armadura do peito
    retangulo(folha, prata, 61, 82, 38, 56, 10)
    poligono(folha, clarear(prata, 0.6), [(66, 88), (73, 88), (69, 118)], contorno=False)

    # Tabardo azul com estrela
    poligono(folha, azul, [(68, 96), (92, 96), (91, 142), (80, 150), (69, 142)])
    poligono(folha, prata, estrela(80, 117, 8, 3.5))
    retangulo(folha, (90, 70, 45), 61, 127, 38, 6)
    retangulo(folha, prata, 77, 126, 6, 8, 1)

    # Escudo com asa
    poligono(folha, prata, [(34, 92), (68, 92), (68, 118), (51, 143), (34, 118)])
    poligono(folha, azul, [(38, 96), (64, 96), (64, 117), (51, 137), (38, 117)], contorno=False)
    poligono(folha, BRANCO, [(42, 114), (58, 102), (60, 108), (55, 111), (59, 115), (48, 120)], contorno=False)

    # Ombreiras
    circulo(folha, prata, (62, 87), 10)
    circulo(folha, prata, (98, 87), 10)
    circulo(folha, azul, (98, 87), 4, contorno=False)

    # Braço e espada
    linha(folha, prata, (98, 92), (110, 116), 9)
    poligono(folha, (232, 236, 250), [(107, 110), (113, 110), (113, 34), (110, 22), (107, 34)])
    linha(folha, BRANCO, (110, 104), (110, 36), 1, contorno=False)
    retangulo(folha, azul, 100, 108, 20, 5, 2)
    retangulo(folha, COURO, 108, 113, 4, 10)
    circulo(folha, prata, (110, 125), 3)
    circulo(folha, prata, (110, 118), 5)

    # Brilho que corre pela lâmina
    brilho_y = 100 - (a / (2 * math.pi)) * 70
    brilho(folha, BRANCO, (110, brilho_y), 4, 160)

    # Asas do elmo (batem de leve)
    poligono(folha, BRANCO, [(65, 58), (44, 40 + s * 2), (50, 48), (40, 47 + s * 2), (49, 54), (44, 58 + s), (61, 64)])
    poligono(folha, BRANCO, [(95, 58), (116, 40 + s * 2), (110, 48), (120, 47 + s * 2), (111, 54), (116, 58 + s), (99, 64)])

    # Elmo com viseira em T e crista azul
    circulo(folha, prata, (80, 62), 17)
    retangulo(folha, azul, 77, 43, 6, 14, 2)
    retangulo(folha, (20, 20, 35), 70, 58, 24, 5, contorno=False)
    retangulo(folha, (20, 20, 35), 82, 58, 4, 14, contorno=False)
    poligono(folha, clarear(prata, 0.6), [(70, 50), (75, 48), (72, 56)], contorno=False)


# ============================================================
# BÁRBARO: nórdico com pele de urso e pintura de guerra azul
# ============================================================

def desenhar_arma_barbaro(folha, arma):
    metal = (180, 185, 200)

    if arma == "Espada":
        poligono(folha, (222, 228, 242), [(109, 112), (118, 112), (118, 34), (113.5, 20), (109, 34)])
        linha(folha, BRANCO, (113.5, 106), (113.5, 36), 1, contorno=False)
        retangulo(folha, (110, 110, 125), 102, 109, 23, 6, 2)
        retangulo(folha, COURO, 111, 115, 5, 14)

    elif arma == "Machado":
        linha(folha, COURO, (113, 40), (113, 170), 5)
        poligono(folha, metal, [(113, 44), (138, 28), (143, 54), (138, 80), (113, 66)])
        poligono(folha, metal, [(113, 46), (96, 38), (93, 55), (96, 72), (113, 64)])
        linha(folha, clarear(metal, 0.6), (139, 32), (141, 76), 2, contorno=False)
        retangulo(folha, (110, 110, 125), 109, 44, 8, 24, 2)

    elif arma == "Martelo":
        linha(folha, COURO, (113, 50), (113, 168), 5)
        retangulo(folha, metal, 94, 30, 38, 26, 4)
        retangulo(folha, clarear(metal, 0.5), 98, 33, 30, 5, 2, contorno=False)
        retangulo(folha, (110, 110, 125), 110, 30, 6, 26, contorno=False)


def desenhar_barbaro(folha, a, arma):
    pele = (225, 175, 130)
    pele_escura = escurecer(pele, 0.8)
    urso = (115, 78, 48)
    urso_escuro = escurecer(urso, 0.7)
    pintura = (60, 125, 225)
    barba = (235, 195, 95)
    s = math.sin(a)

    # Pele de urso caindo pelas costas
    poligono(folha, urso_escuro, [(62, 62), (98, 62), (104 + s * 3, 160), (80, 154), (56 + s * 2, 160)])

    # Pernas, faixas e botas de pele
    retangulo(folha, escurecer(COURO), 68, 132, 13, 44, 3)
    retangulo(folha, COURO, 82, 132, 13, 44, 3)
    for y in (148, 158):
        linha(folha, escurecer(COURO, 0.6), (68, y), (81, y + 3), 1, contorno=False)
        linha(folha, escurecer(COURO, 0.6), (82, y), (95, y + 3), 1, contorno=False)
    retangulo(folha, urso, 63, 172, 19, 18, 5)
    retangulo(folha, urso, 80, 172, 20, 18, 5)

    # Braço de trás
    linha(folha, pele_escura, (62, 90), (52, 122), 10)
    circulo(folha, pele_escura, (52, 124), 6)
    linha(folha, pintura, (57, 100), (54, 108), 2, contorno=False)

    # Tronco com pinturas azuis
    poligono(folha, pele, [(58, 82), (102, 82), (97, 134), (63, 134)])
    linha(folha, pele_escura, (80, 98), (80, 126), 1.5, contorno=False)
    linha(folha, pele_escura, (72, 114), (88, 114), 1.2, contorno=False)
    linha(folha, pele_escura, (73, 122), (87, 122), 1.2, contorno=False)
    linha(folha, pintura, (65, 94), (76, 101), 2.5, contorno=False)
    linha(folha, pintura, (95, 94), (84, 101), 2.5, contorno=False)
    linha(folha, pintura, (68, 106), (74, 110), 2, contorno=False)

    # Colar de dentes
    for x in (70, 75, 80, 85, 90):
        poligono(folha, OSSO, [(x - 2, 84), (x + 2, 84), (x, 90)], contorno=False)

    # Cinto e saiote de pele
    retangulo(folha, COURO, 61, 126, 38, 9, 2)
    circulo(folha, OSSO, (80, 130), 4)
    poligono(folha, urso, [(64, 134), (96, 134), (92, 152), (80, 146), (68, 152)])

    # Rosto com pintura e barba trançada
    circulo(folha, pele, (80, 64), 15)
    retangulo(folha, pintura, 71, 59, 22, 5, contorno=False)
    circulo(folha, BRANCO, (87, 61), 2.2, contorno=False)
    circulo(folha, CONTORNO, (88, 61), 1.2, contorno=False)
    poligono(folha, barba, [(68, 68), (93, 68), (90, 82), (84, 88), (76, 88), (70, 82)])
    linha(folha, barba, (77, 86), (76, 100), 3)
    linha(folha, barba, (85, 86), (86, 100), 3)
    circulo(folha, (170, 170, 185), (76, 100), 2)
    circulo(folha, (170, 170, 185), (86, 100), 2)
    linha(folha, CONTORNO, (80, 74), (89, 73), 1.2, contorno=False)

    # Cabeça de urso por cima
    circulo(folha, urso, (68, 38), 5)
    circulo(folha, urso, (82, 34), 5)
    poligono(folha, urso, [(60, 70), (61, 50), (70, 40), (92, 40), (100, 50), (100, 66), (94, 56), (66, 56)])
    elipse(folha, urso, 64, 34, 34, 22)
    elipse(folha, urso_escuro, 92, 40, 16, 10)
    circulo(folha, CONTORNO, (106, 44), 2, contorno=False)
    circulo(folha, (240, 200, 60), (88, 41), 1.5, contorno=False)

    # Arma e braço da frente
    desenhar_arma_barbaro(folha, arma)
    linha(folha, pele, (98, 88), (113, 114), 11)
    linha(folha, pintura, (103, 96), (107, 102), 2, contorno=False)
    retangulo(folha, COURO, 106, 104, 11, 7, 2)
    circulo(folha, pele, (113, 116), 6)


# ============================================================
# PALADINO: armadura branca e dourada, martelo sagrado e auréola
# ============================================================

def desenhar_paladino(folha, a):
    ouro = (238, 196, 80)
    ouro_escuro = escurecer(ouro, 0.7)
    branco = (240, 240, 248)
    s = math.sin(a)

    # Aura dourada
    brilho(folha, (255, 230, 140), (80, 112), 70 + s * 3, 28)

    # Capa branca
    poligono(folha, escurecer(branco, 0.85), [(62, 82), (98, 82), (108 + s * 3, 186), (80, 182), (52 + s * 2, 186)])

    # Pernas e botas
    retangulo(folha, ouro_escuro, 68, 134, 12, 44, 4)
    retangulo(folha, ouro, 81, 134, 12, 44, 4)
    retangulo(folha, branco, 64, 176, 17, 14, 4)
    retangulo(folha, branco, 79, 176, 18, 14, 4)

    # Saia de malha
    poligono(folha, (185, 185, 198), [(62, 126), (98, 126), (97, 148), (63, 148)])

    # Peitoral branco com sol dourado
    retangulo(folha, branco, 61, 82, 38, 48, 10)
    retangulo(folha, ouro, 61, 82, 38, 7, 4)
    for i in range(8):
        angulo = i * math.pi / 4 + a / 4
        linha(folha, ouro, (80 + math.cos(angulo) * 9, 106 + math.sin(angulo) * 9),
              (80 + math.cos(angulo) * 13, 106 + math.sin(angulo) * 13), 1.5, contorno=False)
    circulo(folha, ouro, (80, 106), 7)
    retangulo(folha, ouro_escuro, 61, 124, 38, 6)

    # Ombreiras
    circulo(folha, ouro, (61, 88), 11)
    circulo(folha, ouro, (99, 88), 11)
    circulo(folha, clarear(ouro, 0.6), (96, 84), 3, contorno=False)

    # Martelo sagrado brilhando
    brilho(folha, (255, 240, 160), (110, 37), 20 + s * 3, 70)
    linha(folha, COURO, (110, 44), (110, 142), 4)
    retangulo(folha, ouro, 95, 26, 30, 20, 4)
    retangulo(folha, branco, 107, 26, 6, 20, contorno=False)
    poligono(folha, branco, estrela(110, 36, 4, 1.8, 4), contorno=False)

    # Braço
    linha(folha, branco, (98, 94), (110, 116), 9)
    circulo(folha, ouro, (110, 118), 5)

    # Auréola
    brilho(folha, (255, 240, 160), (80, 36), 16, 60)
    anel(folha, (255, 225, 110), 66, 31 + s, 28, 8, 2)

    # Elmo aberto com rosto
    circulo(folha, ouro, (80, 62), 16)
    elipse(folha, PELE, 71, 55, 20, 19)
    circulo(folha, (60, 110, 200), (86, 62), 1.8, contorno=False)
    linha(folha, CONTORNO, (82, 70), (88, 70), 1, contorno=False)
    poligono(folha, branco, [(80, 46), (68, 28), (74, 28), (86, 44)])


# ============================================================
# ASSASSINA: capuz, máscara, cachecol e duas adagas
# ============================================================

def desenhar_assassina(folha, a):
    roxo = (75, 45, 110)
    roxo_claro = (160, 95, 220)
    preto = (32, 24, 44)
    metal = (215, 215, 230)
    s = math.sin(a)

    # Cachecol voando para trás
    poligono(folha, roxo_claro, [(72, 76), (58 + s * 3, 90), (34 + s * 6, 98), (38 + s * 6, 90), (66, 72)])

    # Pernas e botas
    retangulo(folha, preto, 69, 132, 10, 46, 3)
    retangulo(folha, preto, 81, 132, 10, 46, 3)
    retangulo(folha, roxo, 66, 168, 14, 22, 4)
    retangulo(folha, roxo, 79, 168, 15, 22, 4)

    # Braço de trás com adaga invertida
    linha(folha, preto, (66, 92), (56, 118), 7)
    poligono(folha, metal, [(53, 122), (58, 122), (52, 146)])
    circulo(folha, preto, (55, 120), 4)

    # Corpo, faixa cruzada e cinto com bolsinhas
    poligono(folha, roxo, [(66, 82), (94, 82), (96, 136), (64, 136)])
    linha(folha, preto, (68, 86), (93, 124), 3, contorno=False)
    retangulo(folha, preto, 64, 124, 32, 6)
    retangulo(folha, COURO, 68, 126, 7, 9, 2)
    retangulo(folha, COURO, 86, 126, 7, 9, 2)

    # Braço da frente com adaga apontada
    linha(folha, preto, (94, 92), (110, 108), 7)
    poligono(folha, metal, [(112, 105), (136, 99), (114, 113)])
    linha(folha, BRANCO, (116, 107), (132, 101), 0.8, contorno=False)
    circulo(folha, roxo_claro, (112, 109), 2.5)
    circulo(folha, preto, (110, 110), 4)

    # Cabeça: capuz, máscara e olhos brilhantes
    circulo(folha, preto, (80, 62), 16)
    poligono(folha, preto, [(64, 52), (50, 70), (66, 66)])
    elipse(folha, PELE, 74, 54, 20, 15)
    poligono(folha, roxo, [(73, 63), (97, 61), (95, 74), (76, 74)])
    brilho(folha, roxo_claro, (89, 59), 5 + s, 120)
    circulo(folha, (230, 190, 255), (89, 59), 1.8, contorno=False)
    linha(folha, preto, (83, 55), (93, 55), 1.5, contorno=False)


# ============================================================
# MAGO: jovem de capuz, runas brilhantes e orbe flutuante
# ============================================================

CORES_MAGO = {
    "": ((75, 50, 145), (40, 25, 90), (120, 220, 255)),
    "Fogo": ((155, 35, 35), (60, 15, 25), (255, 150, 50)),
    "Gelo": ((215, 235, 250), (80, 140, 195), (120, 220, 255)),
    "Raio": ((40, 45, 100), (20, 20, 55), (255, 230, 80)),
}


def desenhar_mago(folha, a, elemento):
    manto, escuro, luz = CORES_MAGO.get(elemento, CORES_MAGO[""])
    s = math.sin(a)
    orbe_y = 30 + s * 3

    # Luz do orbe
    brilho(folha, luz, (118, orbe_y), 24, 45)
    brilho(folha, luz, (118, orbe_y), 14, 90)

    # Cajado com forquilha
    linha(folha, (90, 60, 40), (118, 52), (118, 190), 4)
    linha(folha, (90, 60, 40), (118, 52), (112, 42), 2.5)
    linha(folha, (90, 60, 40), (118, 52), (124, 42), 2.5)

    # Capa balançando atrás
    poligono(folha, escuro, [(70, 70), (90, 70), (108 + s * 3, 190), (50 + s * 2, 190)])

    # Manto
    poligono(folha, manto, [(80, 72), (48, 190), (112, 190)])
    poligono(folha, escuro, [(77, 100), (83, 100), (89, 190), (71, 190)], contorno=False)
    poligono(folha, escuro, [(48, 180), (112, 180), (114, 190), (46, 190)])

    # Runas da barra (piscam uma depois da outra)
    for i, x in enumerate((56, 68, 92, 104)):
        intensidade = 0.6 + 0.4 * math.sin(a + i * 1.5)
        runa(folha, x, 185, 3, luz, intensidade)

    # Cinto com joia
    poligono(folha, escuro, [(70, 108), (90, 108), (91, 114), (69, 114)])
    circulo(folha, luz, (80, 111), 3)

    # Braço segurando o cajado
    poligono(folha, manto, [(84, 88), (114, 104), (112, 116), (82, 102)])
    circulo(folha, PELE, (116, 110), 5)

    # Capuz (parte de trás), rosto jovem e capuz (frente)
    circulo(folha, escuro, (80, 60), 18)
    circulo(folha, PELE, (82, 64), 12)
    poligono(folha, (70, 45, 35), [(72, 54), (93, 54), (91, 60), (81, 58), (74, 63)], contorno=False)
    brilho(folha, luz, (88, 64), 5, 110)
    circulo(folha, luz, (88, 64), 2, contorno=False)
    linha(folha, CONTORNO, (85, 71), (89, 71), 0.8, contorno=False)
    poligono(folha, manto, [(62, 72), (63, 48), (80, 40), (97, 46), (101, 58), (93, 51), (80, 49), (72, 56), (70, 76)])
    poligono(folha, manto, [(64, 50), (52, 66), (64, 68)])
    poligono(folha, escuro, [(68, 74), (92, 74), (88, 82), (72, 82)])

    # Orbe flutuando sobre o cajado
    if elemento == "Fogo":
        circulo(folha, (255, 120, 40), (118, orbe_y), 7)
        chama(folha, 118, orbe_y + 2, 18, 12, [(255, 120, 40), (255, 190, 70), (255, 245, 180)], a)
    elif elemento == "Gelo":
        giro = math.cos(a) * 4
        poligono(folha, luz, [(118, orbe_y - 11), (118 + 6 + giro * 0.3, orbe_y), (118, orbe_y + 11), (118 - 6 - giro * 0.3, orbe_y)])
        linha(folha, BRANCO, (116, orbe_y - 5), (116, orbe_y + 3), 1, contorno=False)
    else:
        circulo(folha, luz, (118, orbe_y), 8)
        circulo(folha, clarear(luz, 0.7), (115, orbe_y - 3), 3, contorno=False)
        if elemento == "Raio":
            linha(folha, BRANCO, (112, orbe_y + 8 + s * 2), (108, orbe_y + 14), 1, contorno=False)
            linha(folha, BRANCO, (125, orbe_y - 6), (130, orbe_y - 10 - s * 2), 1, contorno=False)

    # Faíscas girando em volta do orbe
    for k in range(2):
        angulo = a + k * math.pi
        circulo(folha, luz, (118 + math.cos(angulo) * 14, orbe_y + math.sin(angulo) * 5), 1.8, contorno=False)


# ============================================================
# ARQUEIRA: elfa de cabelo longo e capa de folhas
# ============================================================

def desenhar_arqueira(folha, a):
    verde = (60, 150, 95)
    verde_escuro = escurecer(verde, 0.65)
    folhagem = [(95, 175, 75), (70, 145, 60), (125, 195, 90)]
    cabelo = (240, 225, 165)
    madeira = (205, 165, 90)
    s = math.sin(a)

    # Cabelo longo atrás
    poligono(folha, cabelo, [(66, 56), (88, 54), (90 + s * 2, 112), (82, 120), (70 + s * 2, 116), (62, 90)])

    # Capa de folhas
    for i in range(7):
        x = 64 - i * 1.5 + s * (i * 0.6)
        y = 84 + i * 11
        folha_de_arvore(folha, x, y, 1.9 + s * 0.1, 22, 11, folhagem[i % 3])

    # Aljava
    poligono(folha, COURO, [(52, 80), (62, 76), (72, 124), (62, 128)])
    for x in (49, 54, 59):
        linha(folha, (150, 110, 60), (x + 3, 80), (x, 64), 1.2)
        poligono(folha, folhagem[0], [(x, 64), (x - 3, 57), (x + 3, 59)], contorno=False)

    # Pernas e botas altas
    retangulo(folha, verde_escuro, 70, 134, 10, 44, 3)
    retangulo(folha, verde_escuro, 82, 134, 10, 44, 3)
    retangulo(folha, COURO, 67, 160, 14, 30, 4)
    retangulo(folha, COURO, 80, 160, 14, 30, 4)

    # Túnica com folhas
    poligono(folha, verde, [(66, 84), (94, 84), (99, 142), (61, 142)])
    folha_de_arvore(folha, 80, 104, 1.57, 14, 7, folhagem[2])
    retangulo(folha, COURO, 64, 124, 33, 5)
    circulo(folha, OURO, (80, 126), 2.5)

    # Arco élfico e corda puxada
    arco(folha, madeira, 112, 46, 36, 110, -math.pi / 2, math.pi / 2, 3.5)
    circulo(folha, OURO, (130, 47), 2.5)
    circulo(folha, OURO, (130, 155), 2.5)
    linha(folha, BRANCO, (130, 48), (112, 102), 0.8, contorno=False)
    linha(folha, BRANCO, (112, 102), (130, 154), 0.8, contorno=False)
    linha(folha, (150, 110, 60), (110, 102), (154, 102), 1.5, contorno=False)
    poligono(folha, (210, 230, 255), [(152, 98), (159, 102), (152, 106)])

    # Braços com braçadeiras
    linha(folha, verde, (94, 94), (146, 102), 7)
    retangulo(folha, COURO, 134, 98, 8, 8, 2)
    circulo(folha, PELE, (147, 102), 4.5)
    linha(folha, verde_escuro, (90, 98), (110, 102), 7)
    circulo(folha, PELE, (112, 102), 4.5)

    # Cabeça, orelha pontuda, cabelo e diadema
    circulo(folha, PELE, (80, 64), 13)
    poligono(folha, PELE, [(72, 64), (56, 52), (70, 71)])
    poligono(folha, cabelo, [(66, 64), (67, 50), (80, 45), (93, 50), (95, 58), (86, 53), (78, 56), (72, 62)])
    circulo(folha, (50, 150, 90), (86, 64), 2, contorno=False)
    circulo(folha, BRANCO, (86.6, 63.4), 0.7, contorno=False)
    linha(folha, OURO, (69, 53), (93, 54), 1.2, contorno=False)
    circulo(folha, (90, 220, 140), (83, 53), 2)


# ============================================================
# GOBLIN: capacete de panela e adaga
# ============================================================

def desenhar_goblin(folha, a):
    verde = (125, 185, 75)
    verde_escuro = escurecer(verde)
    madeira = (150, 110, 70)
    s = math.sin(a)

    # Pernas e pés
    linha(folha, verde_escuro, (72, 150), (70, 181), 7)
    linha(folha, verde, (88, 150), (90, 181), 7)
    elipse(folha, verde_escuro, 61, 179, 16, 9)
    elipse(folha, verde_escuro, 85, 179, 16, 9)

    # Braço de trás
    linha(folha, verde_escuro, (66, 128), (56, 150), 6)
    circulo(folha, verde_escuro, (56, 152), 4)

    # Corpo com placa de madeira pregada
    elipse(folha, verde, 62, 118, 36, 42)
    retangulo(folha, madeira, 66, 124, 28, 20, 3)
    for x, y in ((69, 127), (91, 127), (69, 141), (91, 141)):
        circulo(folha, (190, 190, 200), (x, y), 1.2, contorno=False)
    poligono(folha, COURO, [(62, 146), (98, 146), (92, 166), (80, 159), (68, 166)])
    retangulo(folha, (90, 60, 35), 68, 146, 8, 8, 2)

    # Adaga curva
    linha(folha, verde, (92, 130), (104, 140), 7)
    poligono(folha, (215, 215, 225), [(104, 135), (126, 122), (129, 126), (107, 142)])
    retangulo(folha, COURO, 100, 136, 6, 6, 2)
    circulo(folha, verde, (104, 140), 5)

    # Orelhas que mexem
    poligono(folha, verde, [(96, 98), (128, 84 + s * 2), (100, 112)])
    poligono(folha, verde, [(64, 98), (32, 86 - s * 2), (60, 112)])
    poligono(folha, (225, 145, 145), [(100, 100), (120, 90 + s * 2), (101, 107)], contorno=False)
    poligono(folha, (225, 145, 145), [(60, 100), (40, 92 - s * 2), (59, 107)], contorno=False)

    # Cabeça
    circulo(folha, verde, (80, 104), 20)
    elipse(folha, (255, 225, 30), 67, 98, 10, 9)
    elipse(folha, (255, 225, 30), 83, 98, 10, 9)
    linha(folha, CONTORNO, (73, 99), (73, 106), 1.3, contorno=False)
    linha(folha, CONTORNO, (89, 99), (89, 106), 1.3, contorno=False)
    poligono(folha, verde, [(81, 104), (96, 110), (81, 113)])
    linha(folha, CONTORNO, (70, 117), (92, 116), 1.5, contorno=False)
    for x in (73, 79, 85):
        poligono(folha, BRANCO, [(x, 116), (x + 4, 116), (x + 2, 121)], contorno=False)

    # Capacete de panela com cabo
    poligono(folha, (155, 155, 168), [(61, 96), (99, 96), (97, 82), (63, 82)])
    retangulo(folha, (130, 130, 145), 58, 93, 44, 5, 2)
    linha(folha, (60, 60, 70), (99, 86), (118, 80), 3)
    poligono(folha, (200, 200, 212), [(66, 85), (72, 85), (70, 93)], contorno=False)


# ============================================================
# ESQUELETO: ossos, espada enferrujada e olhos verdes
# ============================================================

def desenhar_esqueleto(folha, a):
    osso = OSSO
    osso_escuro = escurecer(osso, 0.75)
    ferrugem = (165, 110, 75)
    olho = (90, 255, 170)
    s = math.sin(a)

    # Pernas
    linha(folha, osso_escuro, (73, 140), (70, 184), 4)
    linha(folha, osso, (87, 140), (90, 184), 4)
    circulo(folha, osso, (71, 162), 3.5)
    circulo(folha, osso, (89, 162), 3.5)
    elipse(folha, osso, 62, 182, 14, 7)
    elipse(folha, osso, 84, 182, 14, 7)

    # Escudo redondo de madeira no braço de trás
    linha(folha, osso_escuro, (66, 90), (58, 112), 3.5)
    circulo(folha, (130, 90, 50), (56, 116), 16)
    circulo(folha, (100, 68, 38), (56, 116), 11, contorno=False)
    circulo(folha, (160, 160, 170), (56, 116), 4)

    # Bacia, coluna, costelas e clavícula
    poligono(folha, osso, [(68, 130), (92, 130), (88, 142), (72, 142)])
    linha(folha, osso, (80, 88), (80, 132), 4)
    for i in range(4):
        y = 94 + i * 8
        linha(folha, osso, (80, y), (66, y + 5), 2.5)
        linha(folha, osso, (80, y), (94, y + 5), 2.5)
    linha(folha, osso, (64, 88), (96, 88), 3)

    # Braço da frente e espada enferrujada
    linha(folha, osso, (95, 90), (104, 108), 3.5)
    linha(folha, osso, (104, 108), (110, 118), 3.5)
    poligono(folha, ferrugem, [(107, 114), (113, 114), (113, 46), (110, 38), (107, 46)])
    circulo(folha, escurecer(ferrugem), (110, 70), 1.5, contorno=False)
    circulo(folha, escurecer(ferrugem), (111, 92), 1.2, contorno=False)
    retangulo(folha, (110, 100, 95), 102, 112, 16, 5, 2)
    circulo(folha, osso, (110, 119), 4)

    # Crânio
    circulo(folha, osso, (80, 62), 15)
    retangulo(folha, osso, 72, 70, 17, 9, 2)
    for x in (75, 79, 83, 87):
        linha(folha, CONTORNO, (x, 71), (x, 77), 0.8, contorno=False)
    circulo(folha, CONTORNO, (75, 60), 4.5, contorno=False)
    circulo(folha, CONTORNO, (87, 60), 4.5, contorno=False)
    poligono(folha, CONTORNO, [(81, 64), (79, 69), (83, 69)], contorno=False)

    # Brilho verde dos olhos (pulsa)
    brilho(folha, olho, (87, 60), 6 + s * 1.5, 110)
    circulo(folha, olho, (75, 60), 1.8, contorno=False)
    circulo(folha, olho, (87, 60), 1.8, contorno=False)

    # Elmo velho com chifre quebrado
    poligono(folha, (125, 95, 70), [(64, 56), (96, 56), (94, 46), (80, 42), (66, 46)])
    poligono(folha, OSSO, [(66, 50), (54, 38), (58, 46)])


# ============================================================
# ORC: chefe de guerra com tatuagens e machado duplo
# ============================================================

def desenhar_orc(folha, a):
    pele = (95, 140, 75)
    pele_escura = escurecer(pele)
    tatuagem = (40, 70, 40)
    metal = (150, 150, 165)
    s = math.sin(a)

    # Pernas e botas
    retangulo(folha, escurecer(COURO), 60, 138, 17, 40, 4)
    retangulo(folha, COURO, 83, 138, 17, 40, 4)
    retangulo(folha, (60, 40, 25), 56, 174, 22, 16, 5)
    retangulo(folha, (60, 40, 25), 81, 174, 22, 16, 5)

    # Braço de trás
    linha(folha, pele_escura, (56, 96), (46, 130), 11)
    circulo(folha, pele_escura, (46, 133), 7)

    # Corpo forte com tatuagens tribais
    retangulo(folha, pele, 52, 80, 56, 62, 12)
    poligono(folha, tatuagem, [(60, 92), (68, 100), (60, 108), (64, 100)], contorno=False)
    poligono(folha, tatuagem, [(100, 92), (92, 100), (100, 108), (96, 100)], contorno=False)
    linha(folha, tatuagem, (70, 116), (80, 122), 1.5, contorno=False)
    linha(folha, tatuagem, (90, 116), (80, 122), 1.5, contorno=False)

    # Colar de presas
    for x in (66, 73, 80, 87, 94):
        poligono(folha, OSSO, [(x - 2.5, 86), (x + 2.5, 86), (x, 95)])

    # Cinto e pele nos ombros
    retangulo(folha, COURO, 52, 128, 56, 10, 3)
    circulo(folha, OSSO, (80, 133), 5)
    poligono(folha, (110, 90, 70), [(42, 92), (52, 76), (72, 80), (66, 92)])
    poligono(folha, metal, [(40, 80), (50, 76), (40, 60)])

    # Machado duplo
    linha(folha, COURO, (124, 46), (124, 178), 6)
    poligono(folha, metal, [(124, 54), (148, 38), (154, 66), (148, 94), (124, 80)])
    poligono(folha, metal, [(124, 56), (102, 42), (98, 66), (102, 90), (124, 78)])
    linha(folha, clarear(metal, 0.6), (149, 43), (152, 90), 2, contorno=False)
    retangulo(folha, (100, 100, 115), 119, 52, 10, 30, 2)
    brilho(folha, BRANCO, (150, 50 + (s + 1) * 18), 3, 170)

    # Braço da frente com tatuagem
    linha(folha, pele, (102, 96), (122, 124), 13)
    linha(folha, tatuagem, (108, 104), (114, 112), 2, contorno=False)
    retangulo(folha, COURO, 113, 111, 12, 9, 2)
    circulo(folha, pele, (123, 127), 8)

    # Cabeça: mandíbula, presas, pintura e coque
    circulo(folha, pele, (80, 60), 20)
    elipse(folha, pele, 62, 62, 36, 22)
    linha(folha, (190, 40, 40), (70, 66), (78, 66), 2, contorno=False)
    linha(folha, (190, 40, 40), (84, 66), (94, 66), 2, contorno=False)
    brilho(folha, (255, 60, 30), (88, 57), 6, 90)
    circulo(folha, (255, 80, 40), (88, 57), 2.5, contorno=False)
    circulo(folha, (255, 80, 40), (74, 57), 2.5, contorno=False)
    linha(folha, pele_escura, (68, 51), (94, 52), 3, contorno=False)
    poligono(folha, OSSO, [(69, 79), (75, 79), (72, 63)])
    poligono(folha, OSSO, [(86, 79), (92, 79), (89, 63)])
    circulo(folha, (35, 30, 30), (78, 38), 8)
    linha(folha, OSSO, (70, 34), (88, 30), 1.5)


# ============================================================
# BRUXA DO PÂNTANO: chapéu torto, cajado com chama verde
# ============================================================

def desenhar_bruxa(folha, a):
    pele = (155, 185, 115)
    vestido = (55, 75, 55)
    chapeu = (40, 35, 58)
    roxo = (110, 70, 130)
    chama_verde = [(70, 200, 80), (150, 250, 130), (230, 255, 210)]
    s = math.sin(a)

    # Luz da chama
    brilho(folha, chama_verde[0], (116, 46), 22 + s * 2, 60)

    # Cajado retorcido
    linha(folha, (100, 70, 45), (116, 60), (112, 120), 4)
    linha(folha, (100, 70, 45), (112, 120), (116, 190), 4)
    circulo(folha, (100, 70, 45), (114, 96), 3)
    chama(folha, 116, 58, 22, 12, chama_verde, a)

    # Vestido rasgado
    pontos = [(78, 80), (48 + s * 2, 190), (58, 182), (66 + s * 2, 190), (76, 181),
              (86 + s * 2, 190), (96, 182), (108 + s * 2, 190)]
    poligono(folha, vestido, pontos)
    poligono(folha, escurecer(vestido), [(78, 100), (70, 182), (84, 182)], contorno=False)

    # Xale
    poligono(folha, roxo, [(64, 82), (98, 82), (93, 104), (80, 110), (68, 104)])

    # Braço com garras
    linha(folha, vestido, (90, 92), (110, 100), 7)
    circulo(folha, pele, (112, 100), 5)
    for dy in (-3, 0, 3):
        linha(folha, pele, (115, 100 + dy), (120, 101 + dy * 1.4), 1, contorno=False)

    # Cabelo grisalho
    poligono(folha, (190, 190, 200), [(72, 56), (62, 94), (70, 86), (74, 98), (82, 70)])

    # Rosto: nariz torto com verruga e sorriso
    circulo(folha, pele, (84, 64), 13)
    poligono(folha, pele, [(94, 61), (108, 70), (95, 71)])
    circulo(folha, (90, 100, 60), (103, 68), 1.6, contorno=False)
    circulo(folha, (255, 220, 40), (90, 61), 2.2, contorno=False)
    circulo(folha, CONTORNO, (90.5, 61), 1, contorno=False)
    linha(folha, CONTORNO, (84, 72), (93, 75), 1, contorno=False)

    # Chapéu torto
    elipse(folha, chapeu, 58, 46, 56, 10)
    poligono(folha, chapeu, [(66, 50), (100, 50), (92, 30), (100, 12), (84, 24)])
    poligono(folha, roxo, [(68, 46), (98, 46), (97, 51), (67, 51)])
    retangulo(folha, OURO, 78, 45, 6, 7, 1)

    # Luzinhas verdes flutuando
    for k in range(3):
        angulo = a + k * 2.1
        x = 80 + math.cos(angulo) * 34
        y = 130 + math.sin(angulo * 2) * 12 - k * 10
        brilho(folha, chama_verde[1], (x, y), 4, 90)
        circulo(folha, chama_verde[2], (x, y), 1.4, contorno=False)


# ============================================================
# DRAGÃO: em pé, com o peito brilhando de fogo
# ============================================================

def desenhar_dragao(folha, a):
    vermelho = (195, 50, 40)
    escuro = escurecer(vermelho, 0.6)
    barriga = (240, 170, 90)
    fogo = (255, 150, 40)
    s = math.sin(a)

    # Asa de trás
    poligono(folha, escurecer(escuro), [(78, 84), (40, 12 + s * 4), (54, 34), (64, 18 + s * 3), (74, 40), (90, 80)])

    # Cauda enrolada no chão
    poligono(folha, vermelho, [(62, 160), (30, 178), (8, 172), (4, 158), (14, 166), (34, 168), (58, 150)])
    poligono(folha, escuro, [(4, 158), (0, 148), (10, 152)])

    # Pernas traseiras grossas
    elipse(folha, escuro, 52, 136, 34, 42)
    elipse(folha, vermelho, 82, 142, 32, 38)
    retangulo(folha, escuro, 56, 176, 22, 10, 4)
    retangulo(folha, vermelho, 86, 178, 22, 10, 4)
    for x in (58, 66, 88, 96, 104):
        poligono(folha, OSSO, [(x, 186), (x + 5, 186), (x + 2, 191)], contorno=False)

    # Corpo em pé
    elipse(folha, vermelho, 56, 80, 52, 84)

    # Espinhos nas costas
    for y in (86, 100, 114, 128):
        poligono(folha, escuro, [(60, y), (58, y + 10), (48, y + 2)])

    # Peito com placas e fogo brilhando
    poligono(folha, barriga, [(72, 92), (98, 92), (96, 152), (76, 152)])
    brilho(folha, fogo, (86, 116), 20 + s * 4, 80 + s * 30)
    for y in (104, 116, 128, 140):
        linha(folha, escurecer(barriga, 0.8), (75, y), (97, y), 1, contorno=False)
    linha(folha, (255, 210, 90), (86, 100), (82, 112), 1.5, contorno=False)
    linha(folha, (255, 210, 90), (82, 112), (90, 124), 1.5, contorno=False)
    linha(folha, (255, 210, 90), (90, 124), (85, 136), 1.5, contorno=False)

    # Braço pequeno com garras
    linha(folha, vermelho, (96, 100), (112, 116), 6)
    for dy in (-3, 0, 3):
        poligono(folha, OSSO, [(113, 115 + dy), (119, 117 + dy), (113, 118 + dy)], contorno=False)

    # Pescoço e cabeça
    poligono(folha, vermelho, [(82, 90), (102, 88), (114, 50), (98, 46)])
    poligono(folha, barriga, [(92, 88), (100, 88), (110, 54), (104, 52)], contorno=False)
    elipse(folha, vermelho, 96, 26, 40, 26)
    poligono(folha, vermelho, [(126, 30), (150, 37), (148, 50), (124, 50)])
    linha(folha, CONTORNO, (128, 45), (147, 44), 1.2, contorno=False)
    for x in (130, 136, 142):
        poligono(folha, BRANCO, [(x, 45), (x + 3, 45), (x + 1.5, 49)], contorno=False)
    elipse(folha, (255, 225, 30), 112, 32, 11, 8)
    linha(folha, CONTORNO, (117.5, 33), (117.5, 39), 1.3, contorno=False)
    poligono(folha, OSSO, [(102, 32), (84, 8), (108, 26)])
    poligono(folha, OSSO, [(112, 28), (102, 4), (118, 25)])
    circulo(folha, CONTORNO, (146, 37), 1.5, contorno=False)

    # Fumaça subindo do nariz
    brilho(folha, (130, 130, 130), (150, 30 - (s + 1) * 3), 4, 110)
    brilho(folha, (150, 150, 150), (154, 22 - (s + 1) * 4), 3, 80)

    # Asa da frente com membranas
    pontos = [(72, 88), (16, 22 + s * 5), (32, 44), (34, 22 + s * 4), (50, 46), (58, 28 + s * 3), (80, 84)]
    poligono(folha, escuro, pontos)
    linha(folha, escurecer(escuro), (72, 86), (32, 44), 1.2, contorno=False)
    linha(folha, escurecer(escuro), (76, 86), (50, 46), 1.2, contorno=False)


# ============================================================
# VAMPIRO: conde com capa em asas de morcego
# ============================================================

def desenhar_vampiro(folha, a):
    palido = (232, 228, 240)
    preto = (30, 25, 42)
    vermelho = (165, 20, 45)
    terno = (50, 45, 70)
    s = math.sin(a)

    # Capa aberta como asas de morcego (borda recortada)
    asa = [(66, 80), (28, 72 + s * 4), (12, 100 + s * 3), (26, 104), (22, 128 + s * 2), (40, 126),
           (40, 160), (56, 150), (80, 186), (104, 150), (120, 160), (120, 126), (138, 128 + s * 2),
           (134, 104), (148, 100 + s * 3), (132, 72 + s * 4), (94, 80)]
    poligono(folha, preto, asa)
    poligono(folha, vermelho, [(72, 92), (48, 124), (60, 150), (80, 176), (100, 150), (112, 124), (88, 92)], contorno=False)

    # Pernas e sapatos
    retangulo(folha, terno, 70, 136, 10, 50, 3)
    retangulo(folha, terno, 81, 136, 10, 50, 3)
    elipse(folha, preto, 64, 183, 17, 8)
    elipse(folha, preto, 80, 183, 17, 8)

    # Corpo, colete e medalhão
    retangulo(folha, terno, 66, 86, 28, 54, 5)
    poligono(folha, vermelho, [(68, 92), (92, 92), (90, 128), (70, 128)])
    poligono(folha, BRANCO, [(74, 86), (86, 86), (80, 108)])
    linha(folha, OURO, (72, 92), (80, 112), 1, contorno=False)
    linha(folha, OURO, (88, 92), (80, 112), 1, contorno=False)
    circulo(folha, OURO, (80, 114), 4)
    circulo(folha, vermelho, (80, 114), 2, contorno=False)

    # Gola alta
    poligono(folha, preto, [(56, 92), (62, 46), (76, 88)])
    poligono(folha, preto, [(104, 92), (98, 46), (84, 88)])
    poligono(folha, vermelho, [(60, 88), (63, 56), (73, 86)], contorno=False)
    poligono(folha, vermelho, [(100, 88), (97, 56), (87, 86)], contorno=False)

    # Braço com garras
    linha(folha, terno, (92, 96), (104, 122), 8)
    circulo(folha, palido, (105, 125), 5)
    for dx in (-3, 0, 3):
        linha(folha, palido, (105 + dx, 128), (106 + dx * 1.5, 135), 1, contorno=False)

    # Cabeça
    poligono(folha, palido, [(93, 62), (101, 54), (96, 70)])
    circulo(folha, palido, (80, 64), 14)
    poligono(folha, preto, [(64, 62), (66, 50), (80, 44), (94, 50), (96, 60), (87, 54), (80, 64), (73, 54)])
    brilho(folha, (255, 0, 0), (75, 65), 5 + s, 100)
    brilho(folha, (255, 0, 0), (86, 65), 5 + s, 100)
    circulo(folha, (255, 50, 50), (75, 65), 2, contorno=False)
    circulo(folha, (255, 50, 50), (86, 65), 2, contorno=False)
    linha(folha, CONTORNO, (74, 74), (87, 74), 1, contorno=False)
    poligono(folha, BRANCO, [(75, 74), (78, 74), (76.5, 79)], contorno=False)
    poligono(folha, BRANCO, [(83, 74), (86, 74), (84.5, 79)], contorno=False)


# ============================================================
# ARANHA GIGANTE
# ============================================================

def desenhar_pata(folha, base, joelho, pe, cor):
    linha(folha, cor, base, joelho, 3.2)
    linha(folha, cor, joelho, pe, 2.4)
    circulo(folha, cor, joelho, 2.5)


def desenhar_aranha(folha, a):
    corpo = (60, 42, 68)
    corpo_claro = (95, 70, 108)
    marca = (215, 35, 50)
    veneno = (110, 235, 80)
    s = math.sin(a)

    # Patas de trás (mais escuras)
    patas = [
        ((96, 136), (74, 96), (52, 190)),
        ((100, 138), (90, 92), (76, 190)),
        ((106, 138), (124, 92), (130, 190)),
        ((110, 136), (146, 98), (156, 190)),
    ]
    for i, (base, joelho, pe) in enumerate(patas):
        joelho = (joelho[0] + 6, joelho[1] + math.sin(a + i) * 2)
        desenhar_pata(folha, (base[0] + 6, base[1]), joelho, (pe[0] + 6, pe[1]), escurecer(corpo, 0.7))

    # Abdômen com marca vermelha e pelos
    elipse(folha, corpo, 12, 94 + s, 86, 72)
    elipse(folha, corpo_claro, 24, 102 + s, 30, 18, contorno=False)
    poligono(folha, marca, [(48, 114), (64, 114), (59, 126), (64, 138), (48, 138), (53, 126)])
    for x, y in ((24, 140), (34, 150), (80, 104), (88, 120)):
        linha(folha, escurecer(corpo, 0.6), (x, y), (x - 4, y + 4), 1, contorno=False)

    # Cefalotórax e cabeça
    elipse(folha, corpo_claro, 88, 116, 46, 40)
    elipse(folha, corpo, 118, 122, 30, 28)

    # Muitos olhos vermelhos
    brilho(folha, (255, 30, 30), (132, 130), 10, 60 + s * 30)
    for x, y, r in ((132, 128, 3), (139, 126, 2.5), (126, 126, 2), (134, 135, 2), (141, 133, 1.6), (127, 133, 1.6)):
        circulo(folha, (255, 60, 60), (x, y), r, contorno=False)
        circulo(folha, BRANCO, (x - r * 0.3, y - r * 0.3), r * 0.3, contorno=False)

    # Presas com gota de veneno
    poligono(folha, (230, 220, 200), [(137, 142), (144, 142), (140, 156)])
    poligono(folha, (230, 220, 200), [(128, 143), (134, 143), (130, 154)])
    circulo(folha, veneno, (140, 158 + (s + 1) * 2), 2, contorno=False)

    # Patas da frente
    for i, (base, joelho, pe) in enumerate(patas):
        joelho = (joelho[0], joelho[1] - math.sin(a + i + 1) * 2)
        desenhar_pata(folha, base, joelho, pe, corpo_claro)


# ============================================================
# GOLEM DE PEDRA: blocos de pedra, musgo e runas brilhantes
# ============================================================

def desenhar_golem(folha, a, carregando):
    pedra = (135, 128, 122)
    pedra_escura = escurecer(pedra, 0.7)
    musgo = (90, 145, 65)
    runa_cor = (255, 150, 40) if carregando else (90, 220, 255)
    s = math.sin(a)
    forca = 1.6 if carregando else 1.0

    # Cristais nas costas
    for x, altura in ((56, 30), (66, 40), (76, 28)):
        poligono(folha, clarear(runa_cor, 0.3), [(x - 5, 80), (x + 5, 80), (x, 80 - altura)])

    # Pernas de blocos
    poligono(folha, pedra_escura, [(60, 140), (78, 140), (80, 188), (56, 188)])
    poligono(folha, pedra, [(84, 140), (102, 140), (106, 188), (82, 188)])

    # Corpo
    poligono(folha, pedra, [(46, 80), (114, 76), (120, 130), (100, 146), (58, 146), (40, 128)])
    poligono(folha, clarear(pedra, 0.25), [(52, 84), (80, 82), (70, 96), (50, 100)], contorno=False)

    # Rachaduras e runa no peito (brilham mais quando carregando)
    brilho(folha, runa_cor, (80, 110), (18 + s * 3) * forca, 90 * forca)
    linha(folha, runa_cor, (80, 92), (74, 106), 1.5, contorno=False)
    linha(folha, runa_cor, (74, 106), (84, 120), 1.5, contorno=False)
    linha(folha, runa_cor, (84, 120), (78, 134), 1.5, contorno=False)
    circulo(folha, runa_cor, (80, 110), 5)

    # Musgo
    elipse(folha, musgo, 46, 78, 22, 8, contorno=False)
    elipse(folha, musgo, 96, 74, 18, 7, contorno=False)

    # Ombros, braços e punhos enormes
    circulo(folha, pedra, (46, 86), 16)
    circulo(folha, pedra, (114, 84), 16)
    poligono(folha, pedra_escura, [(30, 92), (48, 92), (48, 132), (28, 132)])
    circulo(folha, pedra_escura, (37, 144), 14)
    poligono(folha, pedra, [(112, 90), (130, 90), (134, 130), (114, 130)])
    circulo(folha, pedra, (126, 144), 15)
    linha(folha, runa_cor, (120, 140), (130, 146), 1.2, contorno=False)

    # Cabeça pequena com olhos brilhantes
    poligono(folha, pedra, [(68, 50), (92, 50), (97, 74), (63, 74)])
    brilho(folha, runa_cor, (80, 63), 12 * forca, 70 * forca)
    retangulo(folha, runa_cor, 69, 59, 8, 4, contorno=False)
    retangulo(folha, runa_cor, 84, 59, 8, 4, contorno=False)


# ============================================================
# LORDE SOMBRIO: rei lich flutuando com fogo azul
# ============================================================

def desenhar_lich(folha, a):
    osso = OSSO
    manto = (48, 32, 75)
    manto_escuro = (25, 15, 45)
    fogo_azul = [(40, 90, 255), (110, 190, 255), (230, 250, 255)]
    s = math.sin(a)

    # Aura sombria
    brilho(folha, (120, 60, 220), (80, 108), 78, 30)
    brilho(folha, (140, 70, 230), (80, 108), 58 + s * 3, 40)

    # Manto rasgado (não toca o chão: ele flutua)
    pontos = [(80, 68), (34, 158), (42 + s * 3, 178), (52, 164), (60 + s * 2, 182), (70, 166), (80 + s * 3, 186),
              (90, 166), (100 + s * 2, 182), (108, 164), (124 + s * 3, 176), (120, 150)]
    poligono(folha, manto, pontos)
    poligono(folha, manto_escuro, [(80, 90), (60, 166), (100, 166)], contorno=False)

    # Costelas aparecendo no peito
    poligono(folha, manto_escuro, [(70, 82), (90, 82), (88, 122), (72, 122)])
    linha(folha, osso, (80, 86), (80, 118), 2, contorno=False)
    for y in (92, 100, 108):
        linha(folha, osso, (80, y), (73, y + 4), 1.5, contorno=False)
        linha(folha, osso, (80, y), (87, y + 4), 1.5, contorno=False)

    # Gola alta pontuda
    poligono(folha, manto, [(60, 86), (52, 52), (72, 78)])
    poligono(folha, manto, [(100, 86), (108, 52), (88, 78)])

    # Ombreiras de crânio
    for x in (62, 98):
        circulo(folha, osso, (x, 86), 8)
        circulo(folha, CONTORNO, (x - 3, 85), 1.8, contorno=False)
        circulo(folha, CONTORNO, (x + 3, 85), 1.8, contorno=False)

    # Mão de trás com magia azul
    brilho(folha, fogo_azul[1], (50, 118), 10 + s * 2, 100)
    linha(folha, manto, (62, 94), (52, 116), 7)
    circulo(folha, osso, (50, 118), 4)

    # Cajado com crânio e chama azul
    linha(folha, (60, 40, 75), (116, 34), (116, 168), 4)
    circulo(folha, osso, (116, 32), 7)
    circulo(folha, CONTORNO, (113, 31), 1.8, contorno=False)
    circulo(folha, CONTORNO, (119, 31), 1.8, contorno=False)
    brilho(folha, fogo_azul[0], (116, 18), 16, 70)
    chama(folha, 116, 26, 22, 14, fogo_azul, a)

    # Braço segurando o cajado
    linha(folha, manto, (98, 92), (112, 108), 8)
    circulo(folha, osso, (114, 110), 4)
    for dy in (-3, 0, 3):
        linha(folha, osso, (116, 110 + dy), (120, 110 + dy), 1, contorno=False)

    # Crânio com olhos de fogo azul
    circulo(folha, osso, (80, 60), 14)
    retangulo(folha, osso, 73, 68, 15, 8, 2)
    for x in (76, 80, 84):
        linha(folha, CONTORNO, (x, 69), (x, 75), 0.8, contorno=False)
    circulo(folha, CONTORNO, (75, 58), 4, contorno=False)
    circulo(folha, CONTORNO, (86, 58), 4, contorno=False)
    poligono(folha, CONTORNO, [(80.5, 62), (78.5, 67), (82.5, 67)], contorno=False)
    chama(folha, 75, 61, 10 + s * 2, 6, fogo_azul, a)
    chama(folha, 86, 61, 10 - s * 2, 6, fogo_azul, a + 1)

    # Coroa flutuando
    coroa_y = -s * 2
    poligono(folha, OURO, [(64, 46 + coroa_y), (96, 46 + coroa_y), (100, 26 + coroa_y), (90, 38 + coroa_y),
                           (85, 20 + coroa_y), (80, 34 + coroa_y), (75, 20 + coroa_y), (70, 38 + coroa_y),
                           (60, 26 + coroa_y)])
    circulo(folha, fogo_azul[1], (80, 41 + coroa_y), 2.5)


# ============================================================
# GENÉRICO (inimigos sem desenho próprio)
# ============================================================

def desenhar_generico(folha):
    cinza = (130, 130, 140)
    retangulo(folha, cinza, 62, 85, 36, 100, 8)
    circulo(folha, cinza, (80, 68), 16)
    circulo(folha, (240, 30, 30), (75, 66), 2, contorno=False)
    circulo(folha, (240, 30, 30), (86, 66), 2, contorno=False)
