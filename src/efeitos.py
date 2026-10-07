import math
import random

import pygame

# Paletas de cores usadas pelos efeitos
FOGO = [(255, 230, 120), (255, 160, 40), (240, 80, 30), (180, 40, 20)]
GELO = [(255, 255, 255), (190, 240, 255), (120, 200, 255)]
RAIO = [(255, 255, 255), (255, 240, 120), (255, 210, 40)]
ROXO = [(230, 180, 255), (180, 90, 250), (120, 40, 200)]
SANGUE = [(255, 80, 80), (200, 20, 40), (130, 10, 30)]
CURA = [(180, 255, 180), (90, 230, 110), (40, 180, 80)]
MANA = [(200, 230, 255), (100, 170, 255), (60, 110, 240)]
DOURADO = [(255, 245, 180), (255, 210, 70), (220, 160, 40)]
PEDRA = [(170, 160, 150), (120, 110, 100), (220, 220, 220)]
MADEIRA = [(200, 150, 90), (140, 95, 50)]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def desenhar_brilho(tela, cor, centro, raio, transparencia):
    """Desenha um círculo semitransparente (luz, clarão)."""
    raio = int(raio)
    if raio <= 0 or transparencia <= 0:
        return

    camada = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    pygame.draw.circle(camada, (*cor[:3], int(min(255, transparencia))), (raio, raio), raio)
    tela.blit(camada, (centro[0] - raio, centro[1] - raio))


def girar(x, y, angulo):
    """Gira o ponto (x, y) em volta de (0, 0)."""
    return (
        x * math.cos(angulo) - y * math.sin(angulo),
        x * math.sin(angulo) + y * math.cos(angulo),
    )


# ============================================================
# PARTÍCULA
# ============================================================

class Particula:
    """Pequeno ponto colorido que se move e diminui até sumir."""

    def __init__(self, x, y, vx, vy, cor, duracao, tamanho, gravidade=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.cor = cor
        self.duracao = duracao
        self.tamanho = tamanho
        self.gravidade = gravidade
        self.tempo = 0

    def atualizar(self, dt):
        self.tempo += dt
        self.vy += self.gravidade * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def viva(self):
        return self.tempo < self.duracao

    def desenhar(self, tela):
        resto = 1 - self.tempo / self.duracao
        raio = max(1, int(self.tamanho * resto))
        pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), raio)


def criar_particulas(x, y, cores, quantidade, velocidade, duracao, tamanho, gravidade=0):
    """Cria partículas saindo de (x, y) para todos os lados."""
    particulas = []

    for _ in range(quantidade):
        angulo = random.uniform(0, 2 * math.pi)
        rapidez = random.uniform(velocidade * 0.3, velocidade)

        particulas.append(Particula(
            x, y,
            math.cos(angulo) * rapidez,
            math.sin(angulo) * rapidez,
            random.choice(cores),
            random.uniform(duracao * 0.5, duracao),
            random.uniform(tamanho * 0.5, tamanho),
            gravidade
        ))

    return particulas


# ============================================================
# CLASSE BASE DOS EFEITOS
# ============================================================

class Efeito:
    """Classe base de todo efeito visual.

    - duracao: quanto tempo (em segundos) o efeito fica na tela.
    - atraso: quanto tempo esperar antes de começar.
    - proximos: efeitos que começam quando este terminar
      (ex.: a explosão que aparece quando a bola de fogo chega).
    - bloqueia: se True, o jogador espera o efeito acabar para jogar.
    """

    bloqueia = True

    def __init__(self, duracao, atraso=0):
        self.duracao = duracao
        self.tempo = -atraso
        self.proximos = []

    def atualizar(self, dt):
        self.tempo += dt

    def ativo(self):
        return self.tempo >= 0

    def terminou(self):
        return self.tempo >= self.duracao

    def progresso(self):
        # 0.0 no começo e 1.0 no fim
        return max(0.0, min(1.0, self.tempo / self.duracao))

    def desenhar(self, tela):
        pass


# ============================================================
# EFEITOS
# ============================================================

class Explosao(Efeito):
    """Clarão no centro e partículas voando para todos os lados."""

    def __init__(self, x, y, cores, quantidade=30, raio=50, atraso=0):
        super().__init__(0.8, atraso)
        self.x = x
        self.y = y
        self.cores = cores
        self.quantidade = quantidade
        self.raio = raio
        self.particulas = []
        self.criada = False

    def atualizar(self, dt):
        super().atualizar(dt)
        if not self.ativo():
            return

        if not self.criada:
            self.particulas = criar_particulas(
                self.x, self.y, self.cores, self.quantidade,
                self.raio * 5, 0.7, 7, gravidade=250
            )
            self.criada = True

        for particula in self.particulas:
            particula.atualizar(dt)

    def desenhar(self, tela):
        if not self.ativo():
            return

        p = self.progresso()
        if p < 0.4:
            forca = 1 - p / 0.4
            desenhar_brilho(tela, self.cores[-1], (self.x, self.y), self.raio * (0.6 + p * 2), 170 * forca)
            desenhar_brilho(tela, self.cores[0], (self.x, self.y), self.raio * 0.6 * forca + 1, 230)

        for particula in self.particulas:
            if particula.viva():
                particula.desenhar(tela)


class Onda(Efeito):
    """Anel que cresce (onda de choque). Achatada = no chão."""

    def __init__(self, x, y, cor, raio_final=120, atraso=0, achatada=False):
        super().__init__(0.5, atraso)
        self.x = x
        self.y = y
        self.cor = cor
        self.raio_final = raio_final
        self.achatada = achatada

    def desenhar(self, tela):
        if not self.ativo():
            return

        p = self.progresso()
        raio = self.raio_final * p
        espessura = max(1, int(10 * (1 - p)))

        if raio < 6:
            return

        if self.achatada:
            area = pygame.Rect(0, 0, raio * 2, raio * 0.6)
            area.center = (self.x, self.y)
            pygame.draw.ellipse(tela, self.cor, area, min(espessura, int(raio * 0.3)))
        else:
            pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), int(raio), espessura)


class Corte(Efeito):
    """Riscos de golpe (espada, garra) que aparecem e somem."""

    def __init__(self, x, y, cor, tamanho=60, atraso=0, quantidade=3):
        super().__init__(0.35, atraso)
        self.x = x
        self.y = y
        self.cor = cor
        self.tamanho = tamanho
        self.quantidade = quantidade

    def desenhar(self, tela):
        if not self.ativo():
            return

        p = self.progresso()
        crescimento = min(1.0, p * 2.5)
        largura = max(1, int(9 * (1 - p)))

        for i in range(self.quantidade):
            deslocamento = (i - (self.quantidade - 1) / 2) * 18
            inicio = (self.x - self.tamanho / 2, self.y - self.tamanho / 2 + deslocamento)
            fim_total = (self.x + self.tamanho / 2, self.y + self.tamanho / 2 + deslocamento)
            fim = (
                inicio[0] + (fim_total[0] - inicio[0]) * crescimento,
                inicio[1] + (fim_total[1] - inicio[1]) * crescimento,
            )
            pygame.draw.line(tela, self.cor, inicio, fim, largura + 5)
            pygame.draw.line(tela, (255, 255, 255), inicio, fim, largura)


class Projetil(Efeito):
    """Algo que voa de um ponto a outro: bola de energia, flecha, lança de gelo."""

    def __init__(self, inicio, fim, cor, formato="bola", tamanho=10, duracao=0.35,
                 atraso=0, rastro=None, altura_arco=0):
        super().__init__(duracao, atraso)
        self.inicio = inicio
        self.fim = fim
        self.cor = cor
        self.formato = formato
        self.tamanho = tamanho
        self.rastro = rastro or [cor]
        self.altura_arco = altura_arco
        self.particulas = []

    def posicao(self):
        p = self.progresso()
        x = self.inicio[0] + (self.fim[0] - self.inicio[0]) * p
        y = self.inicio[1] + (self.fim[1] - self.inicio[1]) * p
        y -= math.sin(p * math.pi) * self.altura_arco
        return x, y

    def atualizar(self, dt):
        super().atualizar(dt)

        for particula in self.particulas:
            particula.atualizar(dt)

        if self.ativo() and not self.terminou():
            # Deixa um rastro de partículas pelo caminho
            x, y = self.posicao()
            for _ in range(2):
                self.particulas.append(Particula(
                    x, y,
                    random.uniform(-40, 40), random.uniform(-40, 40),
                    random.choice(self.rastro), 0.3, self.tamanho * 0.6
                ))

    def desenhar(self, tela):
        for particula in self.particulas:
            if particula.viva():
                particula.desenhar(tela)

        if not self.ativo():
            return

        x, y = self.posicao()
        angulo = math.atan2(self.fim[1] - self.inicio[1], self.fim[0] - self.inicio[0])

        if self.formato == "bola":
            desenhar_brilho(tela, self.cor, (x, y), self.tamanho * 2.2, 90)
            pygame.draw.circle(tela, self.cor, (int(x), int(y)), int(self.tamanho))
            pygame.draw.circle(tela, (255, 255, 255), (int(x), int(y)), int(self.tamanho * 0.5))

        elif self.formato == "flecha":
            # Haste, ponta de metal e penas, girados na direção do voo
            cauda = girar(-30, 0, angulo)
            pygame.draw.line(tela, (150, 100, 50), (x + cauda[0], y + cauda[1]), (x, y), 3)

            ponta = [girar(8, 0, angulo), girar(-2, -5, angulo), girar(-2, 5, angulo)]
            pygame.draw.polygon(tela, (220, 220, 230), [(x + px, y + py) for px, py in ponta])

            for lado in (-5, 5):
                pena = girar(-34, lado, angulo)
                base = girar(-26, 0, angulo)
                pygame.draw.line(tela, self.cor, (x + base[0], y + base[1]), (x + pena[0], y + pena[1]), 3)

        elif self.formato == "lanca":
            pontos = [girar(24, 0, angulo), girar(0, -7, angulo), girar(-24, 0, angulo), girar(0, 7, angulo)]
            pontos = [(x + px, y + py) for px, py in pontos]
            desenhar_brilho(tela, self.cor, (x, y), 26, 70)
            pygame.draw.polygon(tela, self.cor, pontos)
            pygame.draw.polygon(tela, (255, 255, 255), pontos, 2)


class Raio(Efeito):
    """Relâmpago caindo do céu sobre o alvo."""

    def __init__(self, x, y, atraso=0, cor=(255, 235, 110)):
        super().__init__(0.45, atraso)
        self.x = x
        self.y = y
        self.cor = cor
        self.pontos = []
        self.tempo_para_trocar = 0

    def gerar_caminho(self):
        # Linha em zigue-zague do topo da tela até o alvo
        self.pontos = []
        topo_x = self.x + random.uniform(-50, 50)
        for i in range(9):
            p = i / 8
            x = topo_x + (self.x - topo_x) * p
            if 0 < i < 8:
                x += random.uniform(-20, 20)
            self.pontos.append((x, self.y * p))

    def atualizar(self, dt):
        super().atualizar(dt)
        if not self.ativo():
            return

        # O raio "treme": troca de forma várias vezes
        self.tempo_para_trocar -= dt
        if self.tempo_para_trocar <= 0:
            self.gerar_caminho()
            self.tempo_para_trocar = 0.05

    def desenhar(self, tela):
        if not self.ativo() or not self.pontos:
            return

        forca = 1 - self.progresso()
        desenhar_brilho(tela, self.cor, (self.x, self.y), 70, 140 * forca)
        pygame.draw.lines(tela, self.cor, False, self.pontos, max(2, int(9 * forca)))
        pygame.draw.lines(tela, (255, 255, 255), False, self.pontos, max(1, int(3 * forca)))


class Cristais(Efeito):
    """Cristais de gelo que nascem do chão em volta do alvo."""

    def __init__(self, x, y_chao, atraso=0):
        super().__init__(1.0, atraso)
        self.x = x
        self.y = y_chao

        # Cada cristal: (deslocamento x, altura, largura)
        self.cristais = []
        for _ in range(9):
            self.cristais.append((random.uniform(-70, 70), random.uniform(50, 130), random.uniform(14, 24)))

        # Os mais altos são desenhados primeiro (ficam atrás)
        self.cristais.sort(key=lambda cristal: -cristal[1])

    def desenhar(self, tela):
        if not self.ativo():
            return

        p = self.progresso()
        if p < 0.25:
            crescimento = p / 0.25
        elif p > 0.75:
            crescimento = (1 - p) / 0.25
        else:
            crescimento = 1

        desenhar_brilho(tela, (120, 200, 255), (self.x, self.y - 90), 100, 70 * crescimento)

        for dx, altura, largura in self.cristais:
            base_x = self.x + dx
            pontos = [
                (base_x - largura / 2, self.y),
                (base_x + largura / 2, self.y),
                (base_x + dx * 0.15, self.y - altura * crescimento),
            ]
            pygame.draw.polygon(tela, (160, 225, 255), pontos)
            pygame.draw.polygon(tela, (235, 250, 255), pontos, 2)


class Cura(Efeito):
    """Brilho e partículas subindo (poções, cura do chefe)."""

    def __init__(self, x, y, cores, atraso=0):
        super().__init__(1.0, atraso)
        self.x = x
        self.y = y
        self.cores = cores
        self.particulas = []

    def atualizar(self, dt):
        super().atualizar(dt)
        if not self.ativo():
            return

        if self.tempo < 0.7:
            for _ in range(2):
                self.particulas.append(Particula(
                    self.x + random.uniform(-45, 45), self.y + random.uniform(-10, 80),
                    0, random.uniform(-130, -60),
                    random.choice(self.cores), 0.7, random.uniform(3, 6)
                ))

        for particula in self.particulas:
            particula.atualizar(dt)

    def desenhar(self, tela):
        if not self.ativo():
            return

        desenhar_brilho(tela, self.cores[1], (self.x, self.y + 20), 80, 70 * (1 - self.progresso()))

        for i, particula in enumerate(self.particulas):
            if not particula.viva():
                continue

            if i % 4 == 0:
                # Algumas partículas viram um sinal de "+"
                x, y = int(particula.x), int(particula.y)
                pygame.draw.line(tela, particula.cor, (x - 5, y), (x + 5, y), 3)
                pygame.draw.line(tela, particula.cor, (x, y - 5), (x, y + 5), 3)
            else:
                particula.desenhar(tela)


class Dreno(Efeito):
    """Partículas saindo do alvo e indo até quem suga a vida (vampiro)."""

    def __init__(self, origem, destino, cores, atraso=0):
        super().__init__(0.9, atraso)
        self.origem = origem
        self.destino = destino
        self.cores = cores
        self.particulas = []

    def atualizar(self, dt):
        super().atualizar(dt)
        if not self.ativo():
            return

        if self.tempo < 0.4:
            for _ in range(3):
                x = self.origem[0] + random.uniform(-25, 25)
                y = self.origem[1] + random.uniform(-25, 25)
                self.particulas.append(Particula(
                    x, y,
                    (self.destino[0] - x) / 0.5, (self.destino[1] - y) / 0.5,
                    random.choice(self.cores), 0.5, random.uniform(3, 6)
                ))

        for particula in self.particulas:
            particula.atualizar(dt)

    def desenhar(self, tela):
        for particula in self.particulas:
            if particula.viva():
                particula.desenhar(tela)


class FlashTela(Efeito):
    """A tela inteira pisca com uma cor (acerto crítico, explosão)."""

    def __init__(self, cor, duracao=0.3, atraso=0, transparencia=150):
        super().__init__(duracao, atraso)
        self.cor = cor
        self.transparencia = transparencia

    def desenhar(self, tela):
        if not self.ativo():
            return

        camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        camada.fill((*self.cor, int(self.transparencia * (1 - self.progresso()))))
        tela.blit(camada, (0, 0))


class TextoFlutuante(Efeito):
    """Texto que sobe e some (números de dano, "CRÍTICO!")."""

    bloqueia = False

    def __init__(self, texto, x, y, cor, fonte, atraso=0):
        super().__init__(1.1, atraso)
        self.x = x
        self.y = y
        self.imagem = fonte.render(texto, True, cor)
        self.sombra = fonte.render(texto, True, (0, 0, 0))

    def desenhar(self, tela):
        if not self.ativo():
            return

        p = self.progresso()
        subida = 40 * (1 - (1 - p) ** 2)

        if p < 0.6:
            transparencia = 255
        else:
            transparencia = int(255 * (1 - p) / 0.4)

        x = self.x - self.imagem.get_width() // 2
        y = self.y - subida

        self.sombra.set_alpha(transparencia)
        self.imagem.set_alpha(transparencia)
        tela.blit(self.sombra, (x + 2, y + 2))
        tela.blit(self.imagem, (x, y))


class Confete(Efeito):
    """Chuva de confetes coloridos (vitória)."""

    bloqueia = False

    def __init__(self, largura):
        super().__init__(3.0)
        cores = [(255, 90, 90), (255, 210, 60), (90, 220, 120), (90, 170, 255), (220, 120, 255)]
        self.particulas = []
        for _ in range(120):
            self.particulas.append(Particula(
                random.uniform(0, largura), random.uniform(-300, 0),
                random.uniform(-30, 30), random.uniform(80, 200),
                random.choice(cores), random.uniform(2.0, 3.0), random.uniform(3, 6)
            ))

    def atualizar(self, dt):
        super().atualizar(dt)
        for particula in self.particulas:
            particula.atualizar(dt)

    def desenhar(self, tela):
        for particula in self.particulas:
            if particula.viva():
                particula.desenhar(tela)


# ============================================================
# GERENCIADOR
# ============================================================

class GerenciadorEfeitos:
    """Guarda os efeitos ativos, atualiza e desenha todos."""

    def __init__(self):
        self.lista = []

    def adicionar(self, efeito):
        self.lista.append(efeito)

    def atualizar(self, dt):
        continuam = []

        for efeito in self.lista:
            efeito.atualizar(dt)

            if efeito.terminou():
                # Quando um efeito termina, os "próximos" começam
                continuam += efeito.proximos
            else:
                continuam.append(efeito)

        self.lista = continuam

    def desenhar(self, tela):
        for efeito in self.lista:
            efeito.desenhar(tela)

    def ocupado(self):
        # Existe algum efeito que o jogador precisa esperar?
        for efeito in self.lista:
            if efeito.bloqueia:
                return True
        return False

    def limpar(self):
        self.lista = []
