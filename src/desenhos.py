import math

import pygame

from guerreiro import Guerreiro
from barbaro import Barbaro
from mago import Mago
from arqueiro import Arqueiro
from vampiro import Vampiro
from chefe_final import ChefeFinal

# Cada desenho é pensado numa "folha" de 160 x 200 pixels, com o
# personagem virado para a DIREITA e os pés em y = 190.
#
# Para os desenhos ficarem mais lisos, desenhamos tudo 3 vezes maior
# (SUPER = 3) e depois diminuímos a imagem. Isso suaviza as bordas.
LARGURA_DESENHO = 160
ALTURA_DESENHO = 200
SUPER = 3

CONTORNO = (25, 20, 35)
ESPESSURA = 4          # espessura do contorno na folha grande

PELE = (245, 205, 165)
BRANCO = (245, 245, 250)
OURO = (240, 195, 60)
COURO = (125, 80, 45)
OSSO = (240, 230, 205)

# Guarda os desenhos já prontos para não redesenhar a cada quadro
_cache = {}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def ponto(p):
    # Converte um ponto da folha 160x200 para a folha grande
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


def circulo(folha, cor, centro, raio, contorno=True, metade_de_cima=False):
    centro = ponto(centro)
    raio = round(raio * SUPER)

    if metade_de_cima:
        pygame.draw.circle(folha, cor, centro, raio, draw_top_left=True, draw_top_right=True)
        if contorno:
            pygame.draw.circle(folha, CONTORNO, centro, raio, ESPESSURA,
                               draw_top_left=True, draw_top_right=True)
    else:
        pygame.draw.circle(folha, cor, centro, raio)
        if contorno:
            pygame.draw.circle(folha, CONTORNO, centro, raio, ESPESSURA)


def elipse(folha, cor, x, y, largura, altura, contorno=True):
    retangulo_elipse = (x * SUPER, y * SUPER, largura * SUPER, altura * SUPER)
    pygame.draw.ellipse(folha, cor, retangulo_elipse)
    if contorno:
        pygame.draw.ellipse(folha, CONTORNO, retangulo_elipse, ESPESSURA)


def retangulo(folha, cor, x, y, largura, altura, borda=0, contorno=True):
    ret = (x * SUPER, y * SUPER, largura * SUPER, altura * SUPER)
    pygame.draw.rect(folha, cor, ret, border_radius=borda * SUPER)
    if contorno:
        pygame.draw.rect(folha, CONTORNO, ret, ESPESSURA, border_radius=borda * SUPER)


def linha(folha, cor, inicio, fim, largura, contorno=True):
    # Linha com pontas arredondadas (bom para braços e cabos)
    inicio = ponto(inicio)
    fim = ponto(fim)
    largura = round(largura * SUPER)

    if contorno:
        grossa = largura + ESPESSURA * 2
        pygame.draw.line(folha, CONTORNO, inicio, fim, grossa)
        pygame.draw.circle(folha, CONTORNO, inicio, grossa // 2)
        pygame.draw.circle(folha, CONTORNO, fim, grossa // 2)

    pygame.draw.line(folha, cor, inicio, fim, largura)
    pygame.draw.circle(folha, cor, inicio, largura // 2)
    pygame.draw.circle(folha, cor, fim, largura // 2)


def arco(folha, cor, x, y, largura, altura, angulo_inicial, angulo_final, espessura):
    ret = (x * SUPER, y * SUPER, largura * SUPER, altura * SUPER)
    pygame.draw.arc(folha, CONTORNO, ret, angulo_inicial, angulo_final, round(espessura * SUPER) + ESPESSURA)
    pygame.draw.arc(folha, cor, ret, angulo_inicial, angulo_final, round(espessura * SUPER))


def brilho(folha, cor, centro, raio, transparencia):
    # Círculo semitransparente (aura, luz de cristal...)
    pygame.draw.circle(folha, (*cor[:3], transparencia), ponto(centro), round(raio * SUPER))


# ============================================================
# ESCOLHA DO DESENHO
# ============================================================

def tipo_do_desenho(personagem):
    # A ordem importa: Barbaro antes de Guerreiro não é necessária
    # (são classes diferentes), mas Vampiro e ChefeFinal precisam
    # vir antes da checagem pelo nome, porque também são Inimigo.
    if isinstance(personagem, Barbaro):
        return "barbaro"
    if isinstance(personagem, Guerreiro):
        return "guerreiro"
    if isinstance(personagem, Mago):
        # Os magos elementais têm o atributo "elemento"
        return "mago" + getattr(personagem, "elemento", "")
    if isinstance(personagem, Arqueiro):
        return "arqueiro"
    if isinstance(personagem, Vampiro):
        return "vampiro"
    if isinstance(personagem, ChefeFinal):
        return "chefe"
    if personagem.nome == "Goblin":
        return "goblin"
    if personagem.nome == "Orc":
        return "orc"
    if personagem.nome == "Dragão Jovem":
        return "dragao"
    return "generico"


def criar_desenho(personagem, extra=None, escala=1.0):
    """Devolve uma imagem (Surface) do personagem, virado para a direita.

    - extra: detalhe opcional (ex.: a arma que o bárbaro está segurando).
    - escala: 1.0 = 160 x 200 pixels.
    """
    tipo = tipo_do_desenho(personagem)
    chave = (tipo, extra, escala)

    if chave in _cache:
        return _cache[chave]

    folha = pygame.Surface((LARGURA_DESENHO * SUPER, ALTURA_DESENHO * SUPER), pygame.SRCALPHA)

    if tipo == "guerreiro":
        desenhar_guerreiro(folha)
    elif tipo == "barbaro":
        desenhar_barbaro(folha, extra or "Machado")
    elif tipo.startswith("mago"):
        desenhar_mago(folha, tipo.replace("mago", ""))
    elif tipo == "arqueiro":
        desenhar_arqueiro(folha)
    elif tipo == "goblin":
        desenhar_goblin(folha)
    elif tipo == "orc":
        desenhar_orc(folha)
    elif tipo == "dragao":
        desenhar_dragao(folha)
    elif tipo == "vampiro":
        desenhar_vampiro(folha)
    elif tipo == "chefe":
        desenhar_chefe_final(folha)
    else:
        desenhar_generico(folha)

    tamanho = (int(LARGURA_DESENHO * escala), int(ALTURA_DESENHO * escala))
    imagem = pygame.transform.smoothscale(folha, tamanho)

    _cache[chave] = imagem
    return imagem


# ============================================================
# GUERREIRO
# ============================================================

def desenhar_guerreiro(folha):
    aco = (180, 185, 200)
    aco_escuro = escurecer(aco)
    azul = (45, 85, 180)
    bota = (95, 60, 35)

    # Capa
    poligono(folha, escurecer(azul), [(66, 84), (94, 84), (106, 174), (54, 174)])

    # Pernas e botas
    retangulo(folha, aco_escuro, 69, 134, 11, 46, 3)
    retangulo(folha, aco, 82, 134, 11, 46, 3)
    retangulo(folha, bota, 65, 176, 17, 14, 4)
    retangulo(folha, bota, 80, 176, 18, 14, 4)

    # Armadura do corpo, com brilho
    retangulo(folha, aco, 62, 82, 36, 56, 9)
    retangulo(folha, clarear(aco, 0.5), 66, 88, 6, 34, 3, contorno=False)

    # Túnica azul com emblema
    poligono(folha, azul, [(69, 92), (91, 92), (90, 140), (80, 148), (70, 140)])
    circulo(folha, OURO, (80, 110), 5)

    # Cinto
    retangulo(folha, COURO, 62, 127, 36, 6)
    retangulo(folha, OURO, 77, 126, 6, 8, 1)

    # Escudo (borda dourada e cruz)
    poligono(folha, OURO, [(36, 90), (70, 90), (70, 120), (53, 144), (36, 120)])
    poligono(folha, azul, [(40, 94), (66, 94), (66, 118), (53, 138), (40, 118)], contorno=False)
    retangulo(folha, OURO, 51, 98, 4, 32, contorno=False)
    retangulo(folha, OURO, 43, 107, 20, 4, contorno=False)

    # Ombreiras
    circulo(folha, aco, (63, 86), 9)
    circulo(folha, aco, (97, 86), 9)
    circulo(folha, clarear(aco, 0.5), (95, 83), 3, contorno=False)

    # Braço da espada
    linha(folha, aco, (97, 90), (108, 116), 9)

    # Espada
    poligono(folha, (225, 230, 245), [(105, 110), (111, 110), (111, 38), (108, 26), (105, 38)])
    linha(folha, BRANCO, (107.5, 104), (107.5, 40), 1, contorno=False)
    retangulo(folha, OURO, 99, 108, 18, 5, 2)
    retangulo(folha, COURO, 106, 113, 4, 10)
    circulo(folha, OURO, (108, 125), 3)
    circulo(folha, PELE, (108, 117), 5)

    # Elmo com viseira
    circulo(folha, aco, (80, 62), 17)
    retangulo(folha, clarear(aco, 0.5), 71, 48, 6, 9, 2, contorno=False)
    retangulo(folha, CONTORNO, 70, 59, 25, 7, 2, contorno=False)
    retangulo(folha, aco_escuro, 79, 66, 4, 11, contorno=False)

    # Penacho
    poligono(folha, (215, 40, 45), [(76, 46), (84, 46), (74, 24), (62, 30)])
    poligono(folha, (250, 90, 90), [(77, 44), (80, 44), (72, 30), (68, 32)], contorno=False)


# ============================================================
# BÁRBARO
# ============================================================

def desenhar_arma_barbaro(folha, arma):
    metal = (175, 180, 195)

    if arma == "Espada":
        poligono(folha, (220, 225, 240), [(109, 112), (118, 112), (118, 34), (113.5, 20), (109, 34)])
        linha(folha, BRANCO, (113.5, 106), (113.5, 36), 1, contorno=False)
        retangulo(folha, (110, 110, 120), 102, 109, 23, 6, 2)
        retangulo(folha, COURO, 111, 115, 5, 14)

    elif arma == "Machado":
        linha(folha, COURO, (113, 40), (113, 170), 5)
        # Lâmina dupla
        poligono(folha, metal, [(113, 44), (138, 28), (143, 54), (138, 80), (113, 66)])
        poligono(folha, metal, [(113, 46), (96, 38), (93, 55), (96, 72), (113, 64)])
        linha(folha, clarear(metal, 0.6), (139, 32), (141, 76), 2, contorno=False)
        retangulo(folha, (110, 110, 120), 109, 44, 8, 24, 2)

    elif arma == "Martelo":
        linha(folha, COURO, (113, 50), (113, 168), 5)
        retangulo(folha, metal, 94, 30, 38, 26, 4)
        retangulo(folha, clarear(metal, 0.5), 98, 33, 30, 5, 2, contorno=False)
        retangulo(folha, (110, 110, 120), 110, 30, 6, 26, contorno=False)


def desenhar_barbaro(folha, arma):
    pele = (225, 170, 120)
    pele_escura = escurecer(pele, 0.8)
    pelo = (165, 150, 135)
    cabelo = (205, 95, 40)
    metal = (160, 160, 175)

    # Cabelo comprido atrás
    poligono(folha, cabelo, [(64, 60), (96, 60), (100, 94), (60, 94)])

    # Pernas e botas de pele
    retangulo(folha, escurecer(COURO), 68, 132, 13, 46, 3)
    retangulo(folha, COURO, 82, 132, 13, 46, 3)
    retangulo(folha, pelo, 63, 172, 19, 18, 5)
    retangulo(folha, pelo, 80, 172, 20, 18, 5)

    # Braço de trás
    linha(folha, pele_escura, (62, 90), (52, 122), 10)
    circulo(folha, pele_escura, (52, 124), 6)

    # Tronco musculoso
    poligono(folha, pele, [(58, 82), (102, 82), (97, 134), (63, 134)])
    linha(folha, pele_escura, (80, 96), (80, 126), 1.5, contorno=False)
    linha(folha, pele_escura, (67, 100), (78, 104), 1.5, contorno=False)
    linha(folha, pele_escura, (93, 100), (82, 104), 1.5, contorno=False)
    linha(folha, pele_escura, (72, 114), (88, 114), 1.2, contorno=False)
    linha(folha, pele_escura, (73, 122), (87, 122), 1.2, contorno=False)

    # Cinto e tanga de pele
    retangulo(folha, COURO, 61, 126, 38, 9, 2)
    circulo(folha, metal, (80, 130), 4)
    poligono(folha, pelo, [(64, 134), (96, 134), (92, 152), (80, 146), (68, 152)])

    # Pele de lobo no ombro
    poligono(folha, pelo, [(56, 78), (78, 78), (98, 122), (88, 128), (60, 96)])
    linha(folha, escurecer(pelo), (66, 84), (84, 112), 1.2, contorno=False)

    # Cabeça e barba ruiva
    circulo(folha, pele, (80, 62), 15)
    poligono(folha, cabelo, [(66, 67), (94, 67), (90, 84), (80, 92), (70, 84)])
    linha(folha, CONTORNO, (80, 74), (89, 73), 1.2, contorno=False)
    circulo(folha, CONTORNO, (87, 63), 2, contorno=False)
    linha(folha, cabelo, (83, 60), (92, 61), 1.8, contorno=False)

    # Elmo com chifres
    poligono(folha, metal, [(63, 58), (97, 58), (95, 47), (80, 40), (65, 47)])
    retangulo(folha, escurecer(metal), 63, 54, 34, 5, contorno=False)
    poligono(folha, OSSO, [(65, 52), (48, 42), (44, 26), (56, 38), (68, 46)])
    poligono(folha, OSSO, [(95, 52), (112, 42), (116, 26), (104, 38), (92, 46)])

    # Arma e braço da frente
    desenhar_arma_barbaro(folha, arma)
    linha(folha, pele, (98, 88), (113, 114), 11)
    retangulo(folha, COURO, 106, 104, 11, 7, 2)
    circulo(folha, pele, (113, 116), 6)


# ============================================================
# MAGO (com cores diferentes para cada elemento)
# ============================================================

CORES_MAGO = {
    "": ((95, 55, 170), (110, 210, 255)),
    "Fogo": ((190, 45, 35), (255, 150, 40)),
    "Gelo": ((55, 135, 205), (190, 245, 255)),
    "Raio": ((70, 45, 150), (255, 230, 70)),
}


def desenhar_mago(folha, elemento):
    manto, cristal = CORES_MAGO.get(elemento, CORES_MAGO[""])

    # Luz do cristal
    brilho(folha, cristal, (116, 42), 24, 55)
    brilho(folha, cristal, (116, 42), 15, 100)

    # Cajado
    linha(folha, COURO, (116, 52), (116, 190), 4)

    # Manto com sombra e barra dourada
    poligono(folha, manto, [(80, 74), (44, 190), (116, 190)])
    poligono(folha, escurecer(manto), [(80, 76), (46, 188), (62, 188)], contorno=False)
    poligono(folha, OURO, [(48, 180), (112, 180), (116, 190), (44, 190)])

    # Detalhes do elemento no manto
    if elemento == "Fogo":
        for x in (52, 64, 76, 88, 100):
            poligono(folha, (255, 160, 50), [(x, 180), (x + 10, 180), (x + 4, 164)], contorno=False)
            poligono(folha, (255, 225, 110), [(x + 3, 180), (x + 7, 180), (x + 4, 171)], contorno=False)
    elif elemento == "Gelo":
        for x, y in ((68, 140), (90, 158), (76, 166), (84, 124)):
            linha(folha, BRANCO, (x - 5, y), (x + 5, y), 1, contorno=False)
            linha(folha, BRANCO, (x, y - 5), (x, y + 5), 1, contorno=False)
            linha(folha, BRANCO, (x - 4, y - 4), (x + 4, y + 4), 1, contorno=False)
            linha(folha, BRANCO, (x - 4, y + 4), (x + 4, y - 4), 1, contorno=False)
    elif elemento == "Raio":
        poligono(folha, cristal, [(84, 120), (72, 146), (82, 146), (74, 172), (94, 138), (83, 138), (90, 120)])
    else:
        for x, y in ((70, 140), (90, 160), (80, 118), (64, 170)):
            circulo(folha, OURO, (x, y), 2.5, contorno=False)

    # Faixa na cintura
    poligono(folha, OURO, [(70, 108), (90, 108), (91, 113), (69, 113)])

    # Braço (manga) segurando o cajado
    poligono(folha, manto, [(84, 88), (112, 106), (109, 118), (81, 102)])
    circulo(folha, PELE, (114, 112), 5)

    # Rosto, barba e bigode
    circulo(folha, PELE, (80, 62), 13)
    poligono(folha, BRANCO, [(67, 66), (93, 66), (88, 90), (80, 100), (72, 90)])
    elipse(folha, BRANCO, 73, 64, 17, 6, contorno=False)
    circulo(folha, CONTORNO, (86, 58), 2, contorno=False)
    linha(folha, BRANCO, (82, 53), (90, 54), 1.5, contorno=False)

    # Chapéu
    elipse(folha, escurecer(manto), 50, 43, 60, 11)
    poligono(folha, manto, [(62, 49), (98, 49), (88, 22), (70, 2), (75, 24)])
    poligono(folha, OURO, [(63, 43), (97, 43), (96, 49), (64, 49)])

    # Cristal na ponta do cajado
    if elemento == "Gelo":
        poligono(folha, cristal, [(116, 28), (124, 42), (116, 56), (108, 42)])
        linha(folha, BRANCO, (114, 36), (114, 46), 1, contorno=False)
    else:
        circulo(folha, cristal, (116, 42), 9)
        circulo(folha, clarear(cristal, 0.7), (113, 39), 3, contorno=False)

    if elemento == "Fogo":
        poligono(folha, (255, 210, 80), [(111, 36), (121, 36), (116, 24)], contorno=False)


# ============================================================
# ARQUEIRO
# ============================================================

def desenhar_arqueiro(folha):
    verde = (55, 145, 75)
    verde_escuro = escurecer(verde)
    bota = (80, 50, 25)

    # Capa
    poligono(folha, verde_escuro, [(66, 80), (92, 80), (100, 166), (58, 166)])

    # Aljava com flechas
    linha(folha, COURO, (50, 82), (44, 64), 1.5)
    linha(folha, COURO, (55, 80), (52, 62), 1.5)
    linha(folha, COURO, (60, 79), (60, 61), 1.5)
    poligono(folha, (215, 50, 50), [(44, 64), (40, 57), (48, 60)])
    poligono(folha, (215, 50, 50), [(52, 62), (49, 55), (56, 58)])
    poligono(folha, (215, 50, 50), [(60, 61), (57, 54), (63, 56)])
    poligono(folha, COURO, [(48, 82), (62, 77), (74, 130), (62, 135)])

    # Pernas e botas
    retangulo(folha, escurecer(COURO), 68, 134, 11, 44, 3)
    retangulo(folha, COURO, 82, 134, 11, 44, 3)
    retangulo(folha, bota, 64, 174, 16, 16, 4)
    retangulo(folha, bota, 80, 174, 17, 16, 4)

    # Túnica, saia e cinto
    retangulo(folha, verde, 63, 86, 34, 50, 7)
    poligono(folha, verde_escuro, [(63, 128), (97, 128), (93, 148), (67, 148)])
    retangulo(folha, COURO, 63, 123, 34, 6)
    retangulo(folha, OURO, 77, 122, 6, 8, 1)
    linha(folha, COURO, (66, 88), (95, 122), 2.5, contorno=False)

    # Arco e corda puxada
    arco(folha, COURO, 112, 48, 36, 108, -math.pi / 2, math.pi / 2, 3.5)
    linha(folha, BRANCO, (130, 50), (112, 102), 0.8, contorno=False)
    linha(folha, BRANCO, (112, 102), (130, 154), 0.8, contorno=False)

    # Flecha pronta para disparar
    linha(folha, COURO, (110, 102), (154, 102), 1.5, contorno=False)
    poligono(folha, (200, 200, 210), [(152, 98), (159, 102), (152, 106)])

    # Braço que segura o arco
    linha(folha, verde, (94, 94), (146, 102), 8)
    circulo(folha, PELE, (147, 102), 5)

    # Braço que puxa a corda
    linha(folha, verde_escuro, (90, 98), (110, 102), 8)
    circulo(folha, PELE, (112, 102), 5)

    # Cabeça e capuz
    circulo(folha, PELE, (80, 64), 13)
    circulo(folha, CONTORNO, (87, 64), 2, contorno=False)
    poligono(folha, (230, 190, 90), [(74, 52), (92, 52), (90, 58), (76, 58)], contorno=False)
    circulo(folha, verde, (80, 60), 16, metade_de_cima=True)
    poligono(folha, verde, [(64, 58), (52, 76), (68, 70)])


# ============================================================
# GOBLIN
# ============================================================

def desenhar_goblin(folha):
    verde = (115, 180, 70)
    verde_escuro = escurecer(verde)

    # Pernas e pés
    linha(folha, verde_escuro, (72, 150), (70, 181), 7)
    linha(folha, verde, (88, 150), (90, 181), 7)
    elipse(folha, verde_escuro, 61, 179, 16, 9)
    elipse(folha, verde_escuro, 85, 179, 16, 9)

    # Braço de trás
    linha(folha, verde_escuro, (66, 128), (56, 150), 6)
    circulo(folha, verde_escuro, (56, 152), 4)

    # Corpo, barriga e tanga
    elipse(folha, verde, 62, 118, 36, 42)
    elipse(folha, clarear(verde, 0.3), 70, 126, 20, 22, contorno=False)
    poligono(folha, COURO, [(62, 146), (98, 146), (92, 166), (80, 159), (68, 166)])

    # Porrete com cravos
    linha(folha, COURO, (100, 148), (124, 102), 6)
    for cravo in ([(121, 90), (131, 90), (126, 77)], [(132, 91), (132, 101), (144, 96)],
                  [(119, 92), (123, 100), (110, 90)]):
        poligono(folha, (205, 205, 215), cravo)
    circulo(folha, escurecer(COURO), (126, 96), 10)

    # Braço da frente
    linha(folha, verde, (92, 130), (101, 148), 7)
    circulo(folha, verde, (101, 149), 5)

    # Orelhas pontudas
    poligono(folha, verde, [(96, 96), (128, 82), (100, 112)])
    poligono(folha, verde, [(64, 96), (34, 84), (60, 112)])
    poligono(folha, (220, 140, 140), [(100, 98), (120, 88), (101, 106)], contorno=False)
    poligono(folha, (220, 140, 140), [(60, 98), (42, 88), (59, 106)], contorno=False)

    # Cabeça
    circulo(folha, verde, (80, 102), 21)

    # Olhos amarelos com pupila em fenda
    elipse(folha, (255, 225, 30), 67, 93, 10, 9)
    elipse(folha, (255, 225, 30), 83, 93, 10, 9)
    linha(folha, CONTORNO, (73, 94), (73, 101), 1.3, contorno=False)
    linha(folha, CONTORNO, (89, 94), (89, 101), 1.3, contorno=False)

    # Sobrancelhas bravas
    linha(folha, verde_escuro, (66, 88), (77, 92), 2, contorno=False)
    linha(folha, verde_escuro, (94, 88), (84, 92), 2, contorno=False)

    # Nariz, boca e dentes
    poligono(folha, verde, [(81, 100), (93, 106), (81, 109)])
    linha(folha, CONTORNO, (70, 114), (92, 113), 1.5, contorno=False)
    poligono(folha, BRANCO, [(74, 113), (78, 113), (76, 118)], contorno=False)
    poligono(folha, BRANCO, [(85, 113), (89, 113), (87, 118)], contorno=False)


# ============================================================
# ORC
# ============================================================

def desenhar_orc(folha):
    pele = (95, 140, 75)
    pele_escura = escurecer(pele)
    metal = (145, 145, 160)

    # Pernas e botas
    retangulo(folha, escurecer(COURO), 60, 138, 17, 40, 4)
    retangulo(folha, COURO, 83, 138, 17, 40, 4)
    retangulo(folha, (60, 40, 25), 56, 174, 22, 16, 5)
    retangulo(folha, (60, 40, 25), 81, 174, 22, 16, 5)

    # Braço de trás
    linha(folha, pele_escura, (56, 96), (46, 130), 11)
    circulo(folha, pele_escura, (46, 133), 7)

    # Corpo forte
    retangulo(folha, pele, 52, 80, 56, 62, 12)
    linha(folha, pele_escura, (80, 92), (80, 124), 1.5, contorno=False)

    # Alça de couro, cinto e fivela de caveira
    linha(folha, COURO, (58, 84), (100, 128), 5)
    retangulo(folha, COURO, 52, 128, 56, 10, 3)
    circulo(folha, OSSO, (80, 133), 5)
    circulo(folha, CONTORNO, (78, 132), 1, contorno=False)
    circulo(folha, CONTORNO, (82, 132), 1, contorno=False)

    # Ombreira com espinhos
    poligono(folha, metal, [(44, 80), (54, 74), (42, 58)])
    poligono(folha, metal, [(56, 74), (64, 74), (60, 56)])
    circulo(folha, metal, (56, 86), 14)
    circulo(folha, clarear(metal, 0.5), (52, 81), 4, contorno=False)

    # Machado
    linha(folha, COURO, (124, 50), (124, 178), 6)
    poligono(folha, metal, [(124, 54), (150, 38), (156, 70), (150, 102), (124, 86)])
    linha(folha, clarear(metal, 0.6), (151, 43), (154, 97), 2, contorno=False)

    # Braço da frente
    linha(folha, pele, (102, 96), (122, 124), 13)
    retangulo(folha, COURO, 113, 111, 12, 9, 2)
    circulo(folha, pele, (123, 127), 8)

    # Cabeça com mandíbula larga
    circulo(folha, pele, (80, 60), 20)
    elipse(folha, pele, 62, 62, 36, 22)

    # Moicano e brinco
    poligono(folha, (35, 30, 30), [(72, 42), (88, 42), (86, 28), (80, 22), (74, 28)])
    circulo(folha, OURO, (61, 68), 3)

    # Olhos vermelhos e sobrancelha
    brilho(folha, (255, 50, 30), (88, 58), 6, 90)
    circulo(folha, (255, 70, 40), (88, 58), 2.5, contorno=False)
    circulo(folha, (255, 70, 40), (74, 58), 2.5, contorno=False)
    linha(folha, pele_escura, (68, 52), (94, 53), 3, contorno=False)

    # Presas
    poligono(folha, OSSO, [(69, 78), (75, 78), (72, 64)])
    poligono(folha, OSSO, [(86, 78), (92, 78), (89, 64)])


# ============================================================
# DRAGÃO
# ============================================================

def desenhar_dragao(folha):
    vermelho = (210, 60, 40)
    escuro = escurecer(vermelho, 0.6)
    barriga = (245, 185, 100)

    # Asa de trás
    poligono(folha, escurecer(escuro), [(80, 112), (58, 30), (72, 50), (92, 38), (100, 108)])

    # Cauda
    poligono(folha, vermelho, [(52, 140), (12, 166), (4, 184), (24, 176), (62, 156)])
    poligono(folha, escuro, [(12, 166), (0, 156), (6, 186)])

    # Perna de trás com garras
    poligono(folha, escuro, [(56, 146), (74, 146), (74, 184), (54, 184)])
    for x in (54, 61, 68):
        poligono(folha, OSSO, [(x, 184), (x + 5, 184), (x + 2, 190)], contorno=False)

    # Corpo e barriga com escamas
    elipse(folha, vermelho, 38, 106, 94, 58)
    elipse(folha, barriga, 62, 122, 58, 38)
    for y in (130, 138, 146):
        linha(folha, escurecer(barriga, 0.85), (68, y), (114, y), 1, contorno=False)

    # Espinhos nas costas
    for x in (46, 60, 74, 88):
        poligono(folha, escuro, [(x, 112), (x + 11, 110), (x + 4, 96)])

    # Perna da frente com garras
    poligono(folha, vermelho, [(92, 148), (110, 148), (112, 184), (92, 184)])
    for x in (92, 99, 106):
        poligono(folha, OSSO, [(x, 184), (x + 5, 184), (x + 2, 190)], contorno=False)

    # Asa da frente com membranas
    poligono(folha, escuro, [(76, 116), (34, 36), (54, 56), (68, 42), (84, 56), (100, 44), (104, 110)])
    linha(folha, escurecer(escuro), (76, 114), (54, 56), 1.2, contorno=False)
    linha(folha, escurecer(escuro), (82, 112), (84, 56), 1.2, contorno=False)

    # Pescoço
    poligono(folha, vermelho, [(100, 126), (124, 120), (136, 76), (114, 78)])
    poligono(folha, barriga, [(110, 122), (122, 118), (131, 82), (123, 82)], contorno=False)

    # Cabeça e focinho
    elipse(folha, vermelho, 106, 50, 46, 30)
    poligono(folha, vermelho, [(140, 56), (159, 63), (156, 76), (136, 78)])
    linha(folha, CONTORNO, (138, 72), (155, 70), 1.2, contorno=False)
    for x in (140, 146, 152):
        poligono(folha, BRANCO, [(x, 71), (x + 3, 71), (x + 1.5, 75)], contorno=False)
    circulo(folha, CONTORNO, (154, 64), 1.5, contorno=False)

    # Olho e chifres
    elipse(folha, (255, 225, 30), 122, 56, 11, 8)
    linha(folha, CONTORNO, (127.5, 57), (127.5, 63), 1.3, contorno=False)
    poligono(folha, OSSO, [(112, 56), (96, 28), (118, 50)])
    poligono(folha, OSSO, [(121, 53), (114, 26), (128, 50)])

    # Fumaça saindo do nariz
    brilho(folha, (120, 120, 120), (158, 56), 4, 120)
    brilho(folha, (140, 140, 140), (157, 48), 3, 90)


# ============================================================
# VAMPIRO
# ============================================================

def desenhar_vampiro(folha):
    palido = (232, 228, 240)
    preto = (30, 25, 42)
    vermelho = (165, 20, 45)
    terno = (50, 45, 68)

    # Capa (fora preta, dentro vermelha)
    poligono(folha, preto, [(80, 76), (36, 192), (124, 192)])
    poligono(folha, vermelho, [(80, 90), (56, 190), (104, 190)], contorno=False)

    # Pernas e sapatos
    retangulo(folha, terno, 70, 136, 10, 52, 3)
    retangulo(folha, terno, 81, 136, 10, 52, 3)
    elipse(folha, preto, 64, 183, 17, 8)
    elipse(folha, preto, 80, 183, 17, 8)

    # Braço de trás
    linha(folha, terno, (68, 96), (58, 124), 8)
    circulo(folha, palido, (57, 127), 5)

    # Corpo, colete, camisa e medalhão
    retangulo(folha, terno, 66, 86, 28, 54, 5)
    poligono(folha, vermelho, [(68, 92), (92, 92), (90, 128), (70, 128)])
    poligono(folha, BRANCO, [(74, 86), (86, 86), (80, 108)])
    linha(folha, OURO, (72, 92), (80, 112), 1, contorno=False)
    linha(folha, OURO, (88, 92), (80, 112), 1, contorno=False)
    circulo(folha, OURO, (80, 114), 4)
    circulo(folha, vermelho, (80, 114), 2, contorno=False)

    # Gola alta
    poligono(folha, preto, [(56, 92), (64, 48), (76, 88)])
    poligono(folha, preto, [(104, 92), (96, 48), (84, 88)])
    poligono(folha, vermelho, [(60, 88), (65, 56), (73, 86)], contorno=False)
    poligono(folha, vermelho, [(100, 88), (95, 56), (87, 86)], contorno=False)

    # Braço da frente com garras
    linha(folha, terno, (92, 96), (104, 124), 8)
    circulo(folha, palido, (105, 127), 5)
    for dx in (-3, 0, 3):
        linha(folha, palido, (105 + dx, 130), (106 + dx * 1.5, 136), 1, contorno=False)

    # Cabeça, orelhas e cabelo em "V"
    poligono(folha, palido, [(93, 62), (101, 54), (96, 70)])
    circulo(folha, palido, (80, 64), 14)
    poligono(folha, preto, [(64, 62), (66, 50), (80, 44), (94, 50), (96, 60), (87, 54), (80, 64), (73, 54)])

    # Olhos vermelhos brilhando
    brilho(folha, (255, 0, 0), (75, 65), 5, 90)
    brilho(folha, (255, 0, 0), (86, 65), 5, 90)
    circulo(folha, (255, 50, 50), (75, 65), 2, contorno=False)
    circulo(folha, (255, 50, 50), (86, 65), 2, contorno=False)

    # Boca e presas
    linha(folha, CONTORNO, (74, 74), (87, 74), 1, contorno=False)
    poligono(folha, BRANCO, [(75, 74), (78, 74), (76.5, 79)], contorno=False)
    poligono(folha, BRANCO, [(83, 74), (86, 74), (84.5, 79)], contorno=False)


# ============================================================
# LORDE SOMBRIO (CHEFE FINAL)
# ============================================================

def desenhar_chefe_final(folha):
    armadura = (45, 40, 62)
    armadura_clara = (85, 75, 110)
    roxo = (175, 85, 245)

    # Aura roxa
    brilho(folha, (140, 40, 210), (80, 112), 79, 35)
    brilho(folha, (160, 60, 230), (80, 112), 62, 45)

    # Capa
    poligono(folha, (115, 15, 35), [(60, 84), (100, 84), (128, 192), (32, 192)])
    poligono(folha, (75, 10, 25), [(60, 86), (70, 86), (52, 190), (34, 190)], contorno=False)

    # Pernas e botas pontudas
    retangulo(folha, armadura, 64, 138, 14, 46, 3)
    retangulo(folha, armadura_clara, 82, 138, 14, 46, 3)
    poligono(folha, armadura, [(60, 182), (80, 182), (80, 190), (56, 190)])
    poligono(folha, armadura, [(80, 182), (100, 182), (106, 190), (80, 190)])

    # Braço de trás
    linha(folha, armadura, (58, 96), (48, 128), 10)
    circulo(folha, armadura_clara, (48, 131), 6)

    # Armadura com joia brilhante
    retangulo(folha, armadura, 56, 80, 48, 64, 8)
    poligono(folha, armadura_clara, [(62, 86), (98, 86), (94, 120), (66, 120)])
    brilho(folha, roxo, (80, 103), 10, 110)
    poligono(folha, roxo, [(80, 94), (87, 103), (80, 112), (73, 103)])
    retangulo(folha, armadura_clara, 56, 128, 48, 8)
    circulo(folha, OSSO, (80, 132), 5)

    # Ombreiras com espinhos
    poligono(folha, armadura, [(44, 82), (58, 78), (44, 54)])
    poligono(folha, armadura, [(102, 78), (116, 82), (116, 54)])
    circulo(folha, armadura_clara, (56, 86), 13)
    circulo(folha, armadura_clara, (104, 86), 13)

    # Espada sombria com brilho
    brilho(folha, roxo, (118, 66), 26, 45)
    poligono(folha, (65, 55, 90), [(114, 114), (122, 114), (122, 26), (118, 10), (114, 26)])
    linha(folha, roxo, (118, 108), (118, 26), 1.5, contorno=False)
    poligono(folha, roxo, [(104, 112), (132, 112), (136, 105), (100, 105)])
    retangulo(folha, armadura, 116, 114, 5, 14)

    # Braço da frente
    linha(folha, armadura, (100, 96), (117, 120), 11)
    circulo(folha, armadura_clara, (118, 122), 6)

    # Elmo, olhos vermelhos e coroa
    circulo(folha, armadura, (80, 62), 18)
    poligono(folha, (10, 5, 15), [(65, 58), (95, 58), (92, 69), (68, 69)], contorno=False)
    brilho(folha, (255, 0, 0), (74, 63), 6, 110)
    brilho(folha, (255, 0, 0), (87, 63), 6, 110)
    circulo(folha, (255, 60, 60), (74, 63), 2, contorno=False)
    circulo(folha, (255, 60, 60), (87, 63), 2, contorno=False)
    poligono(folha, OURO, [(61, 50), (99, 50), (103, 28), (92, 41), (86, 22), (80, 38), (74, 22), (68, 41), (57, 28)])
    circulo(folha, roxo, (80, 45), 3)


# ============================================================
# GENÉRICO (inimigos sem desenho próprio)
# ============================================================

def desenhar_generico(folha):
    cinza = (130, 130, 140)
    retangulo(folha, cinza, 62, 85, 36, 100, 8)
    circulo(folha, cinza, (80, 68), 16)
    circulo(folha, (240, 30, 30), (75, 66), 2, contorno=False)
    circulo(folha, (240, 30, 30), (86, 66), 2, contorno=False)
