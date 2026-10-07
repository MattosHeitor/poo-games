import contextlib
import io
import math
import random

import pygame

from guerreiro import Guerreiro
from barbaro import Barbaro
from mago import Mago
from magos import MagoElemental, MagoFogo, MagoGelo, MagoRaio
from arqueiro import Arqueiro
from arqueiro_flechas import ArqueiroFlechas
from vampiro import Vampiro
from chefe_final import ChefeFinal
from chefe_dificil import ChefeFinalDificil
from item import PocaoVida, PocaoMana, Aljava
from main import INIMIGOS
from desenhos import criar_desenho
from cenarios import criar_cenario, criar_degrade, tipo_de_cenario, AMBIENTE
import efeitos

# ============================================================
# CONFIGURAÇÕES
# ============================================================

WIDTH = 960
HEIGHT = 640

FPS = 60

# Área da batalha (parte de cima da tela)
ARENA_ALTURA = 400
CHAO_Y = 355                 # altura dos pés dos lutadores
X_JOGADOR = 230
X_INIMIGO = 730
ESCALA_LUTADOR = 1.25

# Cores
BRANCO = (255, 255, 255)
CINZA = (160, 155, 185)
CINZA_ESCURO = (90, 85, 115)
DOURADO = (255, 210, 80)
VERMELHO = (240, 70, 70)
VERDE = (90, 220, 110)
AZUL_MANA = (70, 140, 255)
LARANJA_FLECHA = (230, 150, 60)
FUNDO_PAINEL = (22, 18, 40, 225)
BORDA_PAINEL = (120, 100, 190)

# Tecla -> (nome, classe, cor, descrição)
CLASSES = {
    "1": ("Guerreiro", Guerreiro, (90, 150, 255), "Equilibrado e com muita defesa."),
    "2": ("Bárbaro", Barbaro, (240, 130, 60), "Escolhe a arma a cada ataque."),
    "3": ("Mago", Mago, (180, 100, 255), "Escolhe o elemento e lança magias."),
    "4": ("Arqueiro", ArqueiroFlechas, (90, 210, 120), "Escolhe o tipo de flecha."),
}

# Tecla -> (classe, cor)
TIPOS_MAGO = {
    "1": (MagoFogo, (255, 120, 50)),
    "2": (MagoGelo, (120, 210, 255)),
    "3": (MagoRaio, (255, 225, 70)),
}

# Mesmos inimigos do main.py, mas com o chefe final mais difícil
INIMIGOS_JOGO = dict(INIMIGOS)
INIMIGOS_JOGO["5"] = ("CHEFE FINAL", lambda: ChefeFinalDificil())

CORES_INIMIGO = {
    "1": (90, 210, 100),
    "2": (240, 200, 60),
    "3": (255, 130, 50),
    "4": (230, 60, 80),
    "5": (180, 90, 255),
}

DESCRICAO_INIMIGO = {
    "1": "Fraco, bom para começar.",
    "2": "Forte e resistente.",
    "3": "Ataque muito alto.",
    "4": "Suga a vida a cada mordida.",
    "5": "Golpe devastador, 20% de crítico e se cura com poções.",
}


# ============================================================
# CRIAÇÃO DO JOGADOR (mesmas regras do main.py)
# ============================================================

def criar_jogador(classe, tipo_mago, nome):
    if classe == "1":
        jogador = Guerreiro(nome or "Arthur")
    elif classe == "2":
        jogador = Barbaro(nome or "Bjorn")
    elif classe == "3":
        ClasseMago = TIPOS_MAGO[tipo_mago][0]
        jogador = ClasseMago(nome or "Merlin")
        jogador.adicionar_item(PocaoMana())
    else:
        jogador = ArqueiroFlechas(nome or "Robin")
        jogador.adicionar_item(Aljava())

    # Itens iniciais de todas as classes
    jogador.adicionar_item(PocaoVida())
    jogador.adicionar_item(PocaoVida())
    return jogador


def nome_da_classe(personagem):
    if isinstance(personagem, Barbaro):
        return "Bárbaro"
    if isinstance(personagem, Guerreiro):
        return "Guerreiro"
    if isinstance(personagem, MagoElemental):
        return f"Mago de {personagem.elemento}"
    if isinstance(personagem, Mago):
        return "Mago"
    if isinstance(personagem, Arqueiro):
        return "Arqueiro"
    return ""


# ============================================================
# GAME
# ============================================================

class Game:

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Jogo de Batalha")

        self.clock = pygame.time.Clock()
        self.running = True
        self.tempo = 0.0

        self.font_mini = pygame.font.Font(None, 19)
        self.font_pequena = pygame.font.Font(None, 22)
        self.font = pygame.font.Font(None, 27)
        self.font_media = pygame.font.Font(None, 36)
        self.font_dano = pygame.font.Font(None, 46)
        self.font_titulo = pygame.font.Font(None, 76)

        # Fundo das telas de menu
        self.fundo_menu = criar_degrade(WIDTH, HEIGHT, (25, 15, 60), (95, 35, 85))
        self.estrelas = []
        for _ in range(80):
            self.estrelas.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(1, 3)))

        # Superfície onde a batalha é desenhada (para poder tremer)
        self.arena = pygame.Surface((WIDTH, ARENA_ALTURA))

        self.reiniciar()

    def reiniciar(self):
        # Telas: "classe", "tipo_mago", "nome", "inimigo", "batalha",
        # "armas", "magias", "flechas", "inventario" e "fim"
        self.tela = "classe"
        self.classe = None
        self.tipo_mago = None
        self.nome = ""
        self.jogador = None
        self.inimigo = None
        self.dificuldade = ""
        self.mensagens = []
        self.resultado = None

        self.efeitos = efeitos.GerenciadorEfeitos()
        self.pendente = None            # (hora, função) a executar depois
        self.arma_barbaro = "Machado"   # arma desenhada na mão do bárbaro
        self.fundo_batalha = None
        self.tipo_cenario = None
        self.ambiente = []

        # Animações: guardam a hora em que começaram
        self.avancos = {}
        self.atingidos = {}
        self.tremor = (0, 0)            # (hora de início, força)

        # Valor "atrasado" das barras de vida (efeito de barra descendo)
        self.barras = {}

    # --------------------------------------------------------
    # MENSAGENS
    # --------------------------------------------------------

    def adicionar_mensagem(self, texto):
        self.mensagens.append(texto)
        self.mensagens = self.mensagens[-30:]

    def executar(self, acao, *argumentos):
        # As classes do jogo usam print().
        # Aqui "capturamos" esses prints para mostrar na tela.
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            resultado = acao(*argumentos)

        for linha in saida.getvalue().splitlines():
            self.adicionar_mensagem(linha)

        return resultado

    # --------------------------------------------------------
    # CONTROLE DO TEMPO
    # --------------------------------------------------------

    def agendar(self, atraso, funcao):
        # Executa "funcao" daqui a "atraso" segundos
        self.pendente = (self.tempo + atraso, funcao)

    def ocupado(self):
        # Enquanto houver algo acontecendo, o jogador espera
        return self.pendente is not None or self.efeitos.ocupado()

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:

                # ESC fecha o jogo
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif self.tela == "classe":
                    self.escolher_classe(event)

                elif self.tela == "tipo_mago":
                    self.escolher_tipo_mago(event)

                elif self.tela == "nome":
                    self.digitar_nome(event)

                elif self.tela == "inimigo":
                    self.escolher_inimigo(event)

                elif self.tela == "fim":
                    self.jogar_novamente(event)

                # Telas da batalha: só aceitam teclas quando nada está acontecendo
                elif self.ocupado():
                    pass

                elif self.tela == "batalha":
                    self.escolher_acao(event)

                elif self.tela == "armas":
                    self.escolher_arma(event)

                elif self.tela == "magias":
                    self.escolher_magia(event)

                elif self.tela == "flechas":
                    self.escolher_flecha(event)

                elif self.tela == "inventario":
                    self.escolher_item(event)

    def escolher_classe(self, event):
        if event.unicode in CLASSES:
            self.classe = event.unicode

            if self.classe == "3":
                self.tela = "tipo_mago"
            else:
                self.tela = "nome"

    def escolher_tipo_mago(self, event):
        if event.unicode in TIPOS_MAGO:
            self.tipo_mago = event.unicode
            self.tela = "nome"

    def digitar_nome(self, event):
        if event.key == pygame.K_RETURN:
            self.jogador = criar_jogador(self.classe, self.tipo_mago, self.nome.strip())
            self.tela = "inimigo"

        elif event.key == pygame.K_BACKSPACE:
            self.nome = self.nome[:-1]

        elif event.unicode.isprintable() and len(self.nome) < 14:
            self.nome += event.unicode

    def escolher_inimigo(self, event):
        if event.unicode in INIMIGOS_JOGO:
            dificuldade, fabrica = INIMIGOS_JOGO[event.unicode]
            self.inimigo = fabrica()
            self.dificuldade = dificuldade

            self.tipo_cenario = tipo_de_cenario(self.inimigo)
            self.fundo_batalha = criar_cenario(self.tipo_cenario)
            self.criar_ambiente()

            self.adicionar_mensagem(f"{self.jogador.nome} VS {self.inimigo.nome}")
            self.tela = "batalha"

    def escolher_acao(self, event):
        tecla = event.unicode
        jogador = self.jogador

        if tecla == "1":
            if isinstance(jogador, Barbaro):
                self.tela = "armas"
            else:
                # O arqueiro sem flechas ataca com a adaga
                if getattr(jogador, "flechas", 1) > 0:
                    detalhe = "normal"
                else:
                    detalhe = "adaga"
                self.jogada(jogador.atacar, self.inimigo, efeito=("atacar", detalhe))

        elif tecla == "2":
            if jogador.inventario:
                self.tela = "inventario"
            else:
                self.adicionar_mensagem("Você não possui itens.")

        elif tecla == "3":
            self.adicionar_mensagem("Você fugiu da batalha!")
            self.resultado = "FUGA"
            self.tela = "fim"

        elif tecla == "4" and jogador.nome_habilidade is not None:
            if not jogador.pode_usar_habilidade():
                self.adicionar_mensagem(jogador.mensagem_sem_recurso)
            elif isinstance(jogador, MagoElemental):
                self.tela = "magias"
            elif isinstance(jogador, ArqueiroFlechas):
                self.tela = "flechas"

    def numero_escolhido(self, event, lista):
        # Devolve a posição (0, 1, 2...) escolhida na lista ou None
        tecla = event.unicode
        if tecla.isdigit() and 1 <= int(tecla) <= len(lista):
            return int(tecla) - 1
        return None

    def escolher_arma(self, event):
        if event.unicode == "0":
            self.tela = "batalha"
            return

        posicao = self.numero_escolhido(event, self.jogador.armas)
        if posicao is not None:
            arma = self.jogador.armas[posicao]
            self.arma_barbaro = arma.nome
            self.jogada(self.jogador.usar_arma, arma, self.inimigo, efeito=("arma", arma.nome))

    def escolher_magia(self, event):
        if event.unicode == "0":
            self.tela = "batalha"
            return

        posicao = self.numero_escolhido(event, self.jogador.magias)
        if posicao is not None:
            magia = self.jogador.magias[posicao]

            if self.jogador.pode_lancar(magia):
                self.jogada(self.jogador.lancar_magia, magia, self.inimigo, efeito=("magia", magia.nome))
            else:
                self.adicionar_mensagem(self.jogador.mensagem_sem_recurso)

    def escolher_flecha(self, event):
        if event.unicode == "0":
            self.tela = "batalha"
            return

        posicao = self.numero_escolhido(event, self.jogador.tipos_flecha)
        if posicao is not None:
            flecha = self.jogador.tipos_flecha[posicao]

            if self.jogador.pode_disparar(flecha):
                self.jogada(self.jogador.disparar, flecha, self.inimigo, efeito=("flecha", flecha.nome))
            else:
                self.adicionar_mensagem(self.jogador.mensagem_sem_recurso)

    def escolher_item(self, event):
        if event.unicode == "0":
            self.tela = "batalha"
            return

        inventario = self.jogador.inventario
        posicao = self.numero_escolhido(event, inventario)

        if posicao is not None:
            item = inventario[posicao]
            self.tela = "batalha"
            vidas = self.guardar_vidas()

            # O item só é consumido (e o turno gasto) se teve efeito
            if self.executar(item.usar, self.jogador):
                inventario.remove(item)
                impacto = self.efeito_do_jogador("item", item.nome)
                self.depois_da_jogada(vidas, impacto)

    def jogar_novamente(self, event):
        if event.unicode.lower() == "s":
            self.reiniciar()
        elif event.unicode.lower() == "n":
            self.running = False

    # --------------------------------------------------------
    # TURNOS
    # --------------------------------------------------------

    def guardar_vidas(self):
        return [(self.jogador, self.jogador.vida), (self.inimigo, self.inimigo.vida)]

    def jogada(self, acao, *argumentos, efeito):
        # Executa a ação do jogador, mostra o efeito e passa o turno
        self.tela = "batalha"
        vidas = self.guardar_vidas()

        self.executar(acao, *argumentos)
        impacto = self.efeito_do_jogador(*efeito)
        self.depois_da_jogada(vidas, impacto)

    def depois_da_jogada(self, vidas, impacto):
        self.mostrar_numeros(vidas, impacto)

        if not self.inimigo.esta_vivo():
            self.agendar(1.1, self.vitoria)
        elif not self.jogador.esta_vivo():
            self.agendar(1.1, self.derrota)
        else:
            self.agendar(1.0, self.turno_do_inimigo)

    def turno_do_inimigo(self):
        vidas = self.guardar_vidas()

        if getattr(self.inimigo, "congelado", False):
            # Congelado: perde este ataque
            self.inimigo.congelado = False
            self.adicionar_mensagem(f"{self.inimigo.nome} está congelado e perdeu o ataque!")
            self.efeitos.adicionar(efeitos.Cristais(X_INIMIGO, CHAO_Y))
            impacto = 0
        else:
            self.executar(self.inimigo.atacar, self.jogador)
            impacto = self.efeito_do_inimigo()

        self.mostrar_numeros(vidas, impacto)

        if not self.jogador.esta_vivo():
            self.agendar(1.1, self.derrota)
        else:
            self.agendar(0.6, self.liberar)

    def liberar(self):
        # Fim da espera: o jogador pode jogar de novo
        pass

    def vitoria(self):
        self.adicionar_mensagem(f"{self.inimigo.nome} foi derrotado!")
        self.resultado = "VITÓRIA!"
        self.tela = "fim"
        self.efeitos.adicionar(efeitos.Confete(WIDTH))

    def derrota(self):
        self.adicionar_mensagem(f"{self.jogador.nome} foi derrotado!")
        self.resultado = "DERROTA..."
        self.tela = "fim"

    # --------------------------------------------------------
    # EFEITOS DOS ATAQUES
    # --------------------------------------------------------

    def x_do(self, personagem):
        if personagem is self.jogador:
            return X_JOGADOR
        return X_INIMIGO

    def centro(self, personagem):
        return (self.x_do(personagem), CHAO_Y - 120)

    def ponta(self, personagem):
        # De onde saem magias e flechas
        direcao = 1 if personagem is self.jogador else -1
        return (self.x_do(personagem) + 70 * direcao, CHAO_Y - 150)

    def avancar(self, personagem):
        self.avancos[id(personagem)] = self.tempo

    def atingir(self, personagem, atraso=0.0):
        self.atingidos[id(personagem)] = self.tempo + atraso

    def tremer(self, forca, atraso=0.0):
        self.tremor = (self.tempo + atraso, forca)

    def mostrar_numeros(self, vidas, atraso):
        # Mostra "-dano" ou "+cura" em cima de quem mudou de vida,
        # no momento em que o golpe acerta (atraso)
        for personagem, vida_antes in vidas:
            diferenca = personagem.vida - vida_antes
            x, y = self.centro(personagem)

            if diferenca < 0:
                texto = efeitos.TextoFlutuante(str(diferenca), x, y - 70, VERMELHO, self.font_dano, atraso)
                self.efeitos.adicionar(texto)
            elif diferenca > 0:
                texto = efeitos.TextoFlutuante(f"+{diferenca}", x, y - 70, VERDE, self.font_dano, atraso)
                self.efeitos.adicionar(texto)

    def efeito_do_jogador(self, tipo, nome=""):
        jogador = self.jogador
        x, y = self.centro(self.inimigo)
        origem = self.ponta(jogador)
        adicionar = self.efeitos.adicionar
        E = efeitos

        if tipo == "item":
            cores = {"Poção de Vida": E.CURA, "Poção de Mana": E.MANA, "Aljava": E.DOURADO}
            cx, cy = self.centro(jogador)
            adicionar(E.Cura(cx, cy, cores.get(nome, E.CURA)))
            return 0.1

        impacto = 0.15   # tempo até o golpe acertar

        if tipo == "atacar":
            if isinstance(jogador, Mago):
                impacto = 0.3
                bola = E.Projetil(origem, (x, y), (200, 130, 255), "bola", 7, impacto, rastro=E.ROXO)
                bola.proximos = [E.Explosao(x, y, E.ROXO, 15, 30)]
                adicionar(bola)
            elif isinstance(jogador, Arqueiro) and nome == "normal":
                impacto = 0.3
                flecha = E.Projetil(origem, (x, y), (220, 60, 60), "flecha", 6, impacto, rastro=E.MADEIRA)
                flecha.proximos = [E.Explosao(x, y, E.MADEIRA, 8, 20)]
                adicionar(flecha)
            else:
                # Guerreiro (espada) ou arqueiro sem flechas (adaga)
                self.avancar(jogador)
                adicionar(E.Corte(x, y, (170, 200, 255), 70, atraso=0.12))

        elif tipo == "arma":
            self.avancar(jogador)
            if nome == "Espada":
                adicionar(E.Corte(x, y, (190, 210, 255), 70, atraso=0.12))
            elif nome == "Machado":
                adicionar(E.Corte(x, y, (255, 150, 60), 95, atraso=0.12, quantidade=2))
                adicionar(E.Explosao(x, y, E.FOGO, 20, 35, atraso=0.12))
                self.tremer(8, 0.12)
            elif nome == "Martelo":
                adicionar(E.Onda(x, CHAO_Y, (230, 220, 200), 150, atraso=0.15, achatada=True))
                adicionar(E.Explosao(x, y + 40, E.PEDRA, 30, 40, atraso=0.15))
                self.tremer(13, 0.15)

        elif tipo == "magia":
            impacto = self.efeito_de_magia(nome, origem, x, y)

        elif tipo == "flecha":
            impacto = self.efeito_de_flecha(nome, origem, x, y)

        self.atingir(self.inimigo, impacto)
        return impacto

    def efeito_de_magia(self, nome, origem, x, y):
        adicionar = self.efeitos.adicionar
        E = efeitos

        if nome == "Bola de Fogo":
            bola = E.Projetil(origem, (x, y), (255, 140, 40), "bola", 15, 0.45, rastro=E.FOGO, altura_arco=50)
            bola.proximos = [E.Explosao(x, y, E.FOGO, 40, 55)]
            adicionar(bola)
            self.tremer(7, 0.45)
            return 0.45

        if nome == "Explosão":
            adicionar(E.Onda(x, y, (255, 180, 70), 170, atraso=0.1))
            adicionar(E.Explosao(x, y, E.FOGO, 70, 90, atraso=0.1))
            adicionar(E.FlashTela((255, 140, 40), 0.35, atraso=0.1, transparencia=120))
            self.tremer(15, 0.1)
            return 0.1

        if nome == "Lança de Gelo":
            lanca = E.Projetil(origem, (x, y), (170, 230, 255), "lanca", 10, 0.3, rastro=E.GELO)
            lanca.proximos = [E.Explosao(x, y, E.GELO, 25, 35)]
            adicionar(lanca)
            return 0.3

        if nome == "Congelar":
            adicionar(E.Cristais(x, CHAO_Y, atraso=0.05))
            return 0.2

        if nome == "Faísca":
            faisca = E.Projetil(origem, (x, y), (255, 235, 90), "bola", 7, 0.2, rastro=E.RAIO)
            faisca.proximos = [E.Explosao(x, y, E.RAIO, 18, 28)]
            adicionar(faisca)
            return 0.2

        if nome == "Tempestade":
            for i in range(3):
                adicionar(E.Raio(x + (i - 1) * 25, y, atraso=i * 0.2))
                adicionar(E.FlashTela((255, 255, 220), 0.15, atraso=i * 0.2, transparencia=80))
            self.tremer(9, 0.1)
            return 0.1

        return 0.15

    def efeito_de_flecha(self, nome, origem, x, y):
        adicionar = self.efeitos.adicionar
        E = efeitos

        if nome == "Flecha de fogo":
            flecha = E.Projetil(origem, (x, y), (255, 120, 40), "flecha", 7, 0.3, rastro=E.FOGO)
            flecha.proximos = [E.Explosao(x, y, E.FOGO, 30, 40)]
            adicionar(flecha)
            return 0.3

        if nome == "Flecha perfurante":
            flecha = E.Projetil(origem, (x, y), (120, 230, 255), "flecha", 6, 0.18, rastro=[(150, 240, 255), (255, 255, 255)])
            flecha.proximos = [E.Onda(x, y, (150, 240, 255), 80)]
            adicionar(flecha)
            return 0.18

        if nome == "Flecha dupla":
            for i in range(2):
                flecha = E.Projetil((origem[0], origem[1] + i * 14), (x, y + i * 14), (220, 60, 60),
                                    "flecha", 6, 0.3, atraso=i * 0.15, rastro=E.MADEIRA)
                flecha.proximos = [E.Explosao(x, y + i * 14, E.MADEIRA, 8, 20)]
                adicionar(flecha)
            return 0.3

        # Flecha comum
        flecha = E.Projetil(origem, (x, y), (220, 60, 60), "flecha", 6, 0.3, rastro=E.MADEIRA)
        flecha.proximos = [E.Explosao(x, y, E.MADEIRA, 8, 20)]
        adicionar(flecha)
        return 0.3

    def efeito_do_inimigo(self):
        inimigo = self.inimigo
        x, y = self.centro(self.jogador)
        adicionar = self.efeitos.adicionar
        E = efeitos
        acao = getattr(inimigo, "ultima_acao", "ataque")

        # Chefe se curando: não avança nem acerta ninguém
        if acao == "cura":
            cx, cy = self.centro(inimigo)
            adicionar(E.Cura(cx, cy, E.CURA))
            return 0.1

        impacto = 0.15
        self.avancar(inimigo)

        if isinstance(inimigo, ChefeFinal):
            if acao == "critico":
                adicionar(E.Corte(x, y, (255, 210, 60), 100, atraso=0.12))
                adicionar(E.Explosao(x, y, E.DOURADO, 35, 45, atraso=0.12))
                adicionar(E.FlashTela((255, 255, 255), 0.3, atraso=0.12, transparencia=170))
                adicionar(E.TextoFlutuante("CRÍTICO!", x, y + 20, DOURADO, self.font_media, atraso=0.12))
                self.tremer(16, 0.12)
            elif acao == "devastador":
                adicionar(E.Onda(x, CHAO_Y, (190, 100, 255), 180, atraso=0.12, achatada=True))
                adicionar(E.Explosao(x, y, E.ROXO, 45, 60, atraso=0.12))
                adicionar(E.TextoFlutuante("DEVASTADOR!", x, y + 20, (200, 130, 255), self.font_media, atraso=0.12))
                self.tremer(12, 0.12)
            else:
                adicionar(E.Corte(x, y, (180, 90, 255), 75, atraso=0.12))

        elif isinstance(inimigo, Vampiro):
            adicionar(E.Corte(x, y, (220, 30, 50), 60, atraso=0.12, quantidade=2))
            adicionar(E.Dreno((x, y), self.centro(inimigo), E.SANGUE, atraso=0.2))

        elif inimigo.nome == "Dragão Jovem":
            impacto = 0.35
            bafo = E.Projetil(self.ponta(inimigo), (x, y), (255, 120, 30), "bola", 16, impacto, rastro=E.FOGO)
            bafo.proximos = [E.Explosao(x, y, E.FOGO, 35, 45)]
            adicionar(bafo)

        else:
            adicionar(E.Corte(x, y, (255, 110, 70), 65, atraso=0.12))

        self.atingir(self.jogador, impacto)
        return impacto

    # --------------------------------------------------------
    # ATUALIZAÇÃO
    # --------------------------------------------------------

    def criar_ambiente(self):
        self.ambiente = []
        if AMBIENTE.get(self.tipo_cenario) is None:
            return

        for _ in range(28):
            self.ambiente.append([random.uniform(0, WIDTH), random.uniform(0, ARENA_ALTURA), random.uniform(0, 6)])

    def update(self, dt):
        self.efeitos.atualizar(dt)

        # Executa a função agendada quando chegar a hora
        if self.pendente is not None and self.tempo >= self.pendente[0]:
            funcao = self.pendente[1]
            self.pendente = None
            funcao()

        # Partículas do cenário
        config = AMBIENTE.get(self.tipo_cenario)
        if config is not None:
            velocidade = config[1]
            for particula in self.ambiente:
                particula[1] -= velocidade * dt
                particula[0] += math.sin(self.tempo + particula[2]) * 15 * dt
                if particula[1] < 0:
                    particula[1] = ARENA_ALTURA
                    particula[0] = random.uniform(0, WIDTH)

        # Barras de vida descem devagar até o valor real
        for personagem in (self.jogador, self.inimigo):
            if personagem is None:
                continue
            atual = self.barras.get(id(personagem), personagem.vida)
            atual += (personagem.vida - atual) * min(1, dt * 3)
            self.barras[id(personagem)] = atual

    # --------------------------------------------------------
    # FUNÇÕES DE DESENHO
    # --------------------------------------------------------

    def escrever(self, texto, x, y, cor=BRANCO, fonte=None, centro=False, direita=False, sombra=True):
        if fonte is None:
            fonte = self.font

        imagem = fonte.render(texto, True, cor)

        if centro:
            x -= imagem.get_width() // 2
        elif direita:
            x -= imagem.get_width()

        if sombra:
            self.screen.blit(fonte.render(texto, True, (0, 0, 0)), (x + 2, y + 2))
        self.screen.blit(imagem, (x, y))

    def escrever_titulo(self, texto, y, cor=DOURADO):
        # Título grande com contorno escuro
        fonte = self.font_titulo
        contorno = fonte.render(texto, True, (40, 15, 50))
        imagem = fonte.render(texto, True, cor)
        x = WIDTH // 2 - imagem.get_width() // 2

        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (3, 4)):
            self.screen.blit(contorno, (x + dx, y + dy))
        self.screen.blit(imagem, (x, y))

    def desenhar_painel(self, x, y, largura, altura, cor_borda=BORDA_PAINEL):
        painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(painel, FUNDO_PAINEL, (0, 0, largura, altura), border_radius=12)
        self.screen.blit(painel, (x, y))
        pygame.draw.rect(self.screen, cor_borda, (x, y, largura, altura), 2, border_radius=12)

    def desenhar_cartao(self, x, y, largura, altura, cor, tecla):
        self.desenhar_painel(x, y, largura, altura, cor)

        # Faixa colorida no topo
        pygame.draw.rect(self.screen, cor, (x, y, largura, 8), border_top_left_radius=12, border_top_right_radius=12)

        # Tecla de atalho num círculo
        pygame.draw.circle(self.screen, cor, (x + 24, y + 30), 15)
        pygame.draw.circle(self.screen, BRANCO, (x + 24, y + 30), 15, 2)
        self.escrever(tecla, x + 24, y + 21, (20, 15, 30), self.font, centro=True, sombra=False)

    def desenhar_barra(self, x, y, largura, altura, atual, maximo, cor, atrasado=None):
        pygame.draw.rect(self.screen, (40, 35, 55), (x, y, largura, altura), border_radius=altura // 2)

        # Parte "atrasada" clara (mostra o dano que acabou de entrar)
        if atrasado is not None and atrasado > atual:
            parte = int(largura * atrasado / maximo)
            pygame.draw.rect(self.screen, (255, 240, 200), (x, y, parte, altura), border_radius=altura // 2)

        cheia = int(largura * max(0, atual) / maximo)
        if cheia > 0:
            pygame.draw.rect(self.screen, cor, (x, y, cheia, altura), border_radius=altura // 2)
            # Brilho na metade de cima
            pygame.draw.rect(self.screen, clarear(cor), (x + 3, y + 2, max(0, cheia - 6), altura // 3),
                             border_radius=altura // 2)

        pygame.draw.rect(self.screen, (15, 10, 25), (x, y, largura, altura), 2, border_radius=altura // 2)

    def desenhar_atributo(self, x, y, largura, rotulo, valor, maximo, cor):
        self.escrever(rotulo, x, y, CINZA, self.font_pequena, sombra=False)
        self.escrever(str(valor), x + largura, y, BRANCO, self.font_pequena, direita=True, sombra=False)
        self.desenhar_barra(x, y + 18, largura, 8, valor, maximo, cor)

    def quebrar_texto(self, texto, largura, fonte):
        # Divide um texto longo em linhas que cabem na largura
        linhas = []
        linha = ""

        for palavra in texto.split(" "):
            teste = palavra if linha == "" else linha + " " + palavra

            if fonte.size(teste)[0] <= largura:
                linha = teste
            else:
                linhas.append(linha)
                linha = palavra

        linhas.append(linha)
        return linhas

    def cor_da_vida(self, personagem):
        porcentagem = personagem.vida / personagem.vida_maxima
        if porcentagem > 0.5:
            return (70, 210, 90)
        if porcentagem > 0.25:
            return (240, 195, 50)
        return (235, 60, 60)

    def balanco(self, x):
        # Pequeno movimento de "respiração" dos personagens
        return math.sin(self.tempo * 2.5 + x) * 3

    def desenhar_fundo_menu(self):
        self.screen.blit(self.fundo_menu, (0, 0))

        for x, y, velocidade in self.estrelas:
            brilho = int(140 + 110 * math.sin(self.tempo * velocidade + x))
            pygame.draw.circle(self.screen, (brilho, brilho, 255), (x, y), 1 if velocidade < 2 else 2)

    # --------------------------------------------------------
    # TELA: ESCOLHA DA CLASSE
    # --------------------------------------------------------

    def desenhar_tela_classe(self):
        self.desenhar_fundo_menu()
        self.escrever_titulo("JOGO DE BATALHA", 22)
        self.escrever("Escolha sua classe", WIDTH // 2, 86, BRANCO, self.font_media, centro=True)

        x = 33
        for tecla, (nome, Classe, cor, descricao) in CLASSES.items():
            personagem = Classe(nome)

            self.desenhar_cartao(x, 125, 210, 440, cor, tecla)

            desenho = criar_desenho(personagem)
            self.screen.blit(desenho, (x + 25, 140 + self.balanco(x)))

            centro = x + 105
            self.escrever(nome, centro, 345, cor, self.font_media, centro=True)

            self.desenhar_atributo(x + 20, 382, 170, "Vida", personagem.vida, 140, (70, 210, 90))
            self.desenhar_atributo(x + 20, 414, 170, "Ataque", personagem.ataque, 30, (240, 90, 70))
            self.desenhar_atributo(x + 20, 446, 170, "Defesa", personagem.defesa, 15, (90, 150, 255))

            y = 485
            for linha in self.quebrar_texto(descricao, 180, self.font_pequena):
                self.escrever(linha, centro, y, BRANCO, self.font_pequena, centro=True)
                y += 20

            x += 228

        self.escrever("Pressione de 1 a 4", WIDTH // 2, 590, DOURADO, self.font, centro=True)

    # --------------------------------------------------------
    # TELA: TIPO DE MAGO
    # --------------------------------------------------------

    def desenhar_tela_tipo_mago(self):
        self.desenhar_fundo_menu()
        self.escrever_titulo("Escolha seu elemento", 22)

        x = 40
        for tecla, (ClasseMago, cor) in TIPOS_MAGO.items():
            mago = ClasseMago("Mago")

            self.desenhar_cartao(x, 110, 280, 470, cor, tecla)

            desenho = criar_desenho(mago)
            self.screen.blit(desenho, (x + 60, 120 + self.balanco(x)))

            centro = x + 140
            self.escrever(f"Mago de {mago.elemento}", centro, 325, cor, self.font_media, centro=True)

            y = 365
            for magia in mago.magias:
                self.escrever(magia.nome, x + 20, y, BRANCO, self.font)
                self.escrever(f"{magia.custo} mana", x + 260, y + 2, AZUL_MANA, self.font_pequena, direita=True)
                y += 24
                for linha in self.quebrar_texto(magia.descricao, 240, self.font_pequena):
                    self.escrever(linha, x + 20, y, CINZA, self.font_pequena, sombra=False)
                    y += 19
                y += 14

            x += 300

        self.escrever("Pressione de 1 a 3", WIDTH // 2, 598, DOURADO, self.font, centro=True)

    # --------------------------------------------------------
    # TELA: NOME DO HERÓI
    # --------------------------------------------------------

    def desenhar_tela_nome(self):
        self.desenhar_fundo_menu()
        self.escrever_titulo("Qual o nome do herói?", 40)

        if self.classe == "3":
            ClasseMago, cor = TIPOS_MAGO[self.tipo_mago]
            personagem = ClasseMago("Mago")
            rotulo = f"Mago de {personagem.elemento}"
        else:
            nome, Classe, cor, descricao = CLASSES[self.classe]
            personagem = Classe(nome)
            rotulo = nome

        self.desenhar_painel(80, 140, 280, 400, cor)
        desenho = criar_desenho(personagem, escala=1.4)
        self.screen.blit(desenho, (108, 160 + self.balanco(0)))
        self.escrever(rotulo, 220, 470, cor, self.font_media, centro=True)

        self.desenhar_painel(420, 260, 460, 80, cor)
        cursor = "|" if int(self.tempo * 2) % 2 == 0 else ""
        self.escrever(self.nome + cursor, 445, 280, BRANCO, self.font_titulo)

        self.escrever("ENTER para confirmar", 420, 370, DOURADO, self.font)
        self.escrever("(vazio usa o nome padrão)", 420, 400, CINZA, self.font_pequena)

    # --------------------------------------------------------
    # TELA: ESCOLHA DO INIMIGO
    # --------------------------------------------------------

    def desenhar_tela_inimigo(self):
        self.desenhar_fundo_menu()
        self.escrever_titulo("Escolha seu adversário", 22)

        x = 20
        for tecla, (dificuldade, fabrica) in INIMIGOS_JOGO.items():
            inimigo = fabrica()
            cor = CORES_INIMIGO[tecla]

            self.desenhar_cartao(x, 100, 176, 480, cor, tecla)

            desenho = criar_desenho(inimigo, escala=0.9)
            desenho = pygame.transform.flip(desenho, True, False)
            self.screen.blit(desenho, (x + 16, 125 + self.balanco(x)))

            centro = x + 88
            self.escrever(inimigo.nome, centro, 315, cor, self.font, centro=True)
            self.escrever(dificuldade, centro, 340, CINZA, self.font_pequena, centro=True)

            self.desenhar_atributo(x + 16, 368, 144, "Vida", inimigo.vida, 160, (70, 210, 90))
            self.desenhar_atributo(x + 16, 400, 144, "Ataque", inimigo.ataque, 30, (240, 90, 70))
            self.desenhar_atributo(x + 16, 432, 144, "Defesa", inimigo.defesa, 15, (90, 150, 255))

            y = 470
            for linha in self.quebrar_texto(DESCRICAO_INIMIGO.get(tecla, ""), 150, self.font_pequena):
                self.escrever(linha, centro, y, BRANCO, self.font_pequena, centro=True)
                y += 20

            x += 186

        self.escrever("Pressione de 1 a 5", WIDTH // 2, 598, DOURADO, self.font, centro=True)

    # --------------------------------------------------------
    # TELA: BATALHA
    # --------------------------------------------------------

    def desenhar_ambiente(self, tela):
        config = AMBIENTE.get(self.tipo_cenario)
        if config is None:
            return

        cor = config[0]
        for x, y, fase in self.ambiente:
            brilho = 0.5 + 0.5 * math.sin(self.tempo * 3 + fase)
            efeitos.desenhar_brilho(tela, cor, (x, y), 6, 70 * brilho)
            pygame.draw.circle(tela, cor, (int(x), int(y)), 2)

    def desenhar_lutador(self, tela, personagem, x, direcao):
        extra = self.arma_barbaro if isinstance(personagem, Barbaro) else None
        desenho = criar_desenho(personagem, extra, ESCALA_LUTADOR)

        if direcao < 0:
            desenho = pygame.transform.flip(desenho, True, False)

        dx = 0
        dy = 0

        # Avanço do ataque
        inicio = self.avancos.get(id(personagem))
        if inicio is not None:
            p = (self.tempo - inicio) / 0.4
            if 0 <= p < 1:
                dx += math.sin(math.pi * p) * 50 * direcao

        # Piscar vermelho e tremer ao ser atingido
        inicio = self.atingidos.get(id(personagem))
        if inicio is not None and 0 <= self.tempo - inicio < 0.35:
            dx += random.randint(-6, 6)
            desenho = desenho.copy()
            desenho.fill((140, 110, 110), special_flags=pygame.BLEND_RGB_ADD)

        # Congelado fica azulado
        if getattr(personagem, "congelado", False):
            desenho = desenho.copy()
            desenho.fill((0, 50, 110), special_flags=pygame.BLEND_RGB_ADD)

        # Sombra no chão
        sombra = pygame.Surface((120, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 90), (0, 0, 120, 24))
        tela.blit(sombra, (x - 60 + dx, CHAO_Y - 12))

        if personagem.esta_vivo():
            dy = self.balanco(x)
            tela.blit(desenho, (x - desenho.get_width() // 2 + dx, CHAO_Y - desenho.get_height() * 0.95 + dy))
        else:
            # Derrotado: deitado e meio transparente
            caido = pygame.transform.rotate(desenho, 90 * direcao)
            caido.set_alpha(170)
            tela.blit(caido, (x - caido.get_width() // 2, CHAO_Y - caido.get_height() + 15))

    def desenhar_status(self, personagem, x, cor_nome, subtitulo):
        self.desenhar_painel(x, 12, 330, 100)

        self.escrever(personagem.nome, x + 14, 22, cor_nome, self.font_media)
        self.escrever(subtitulo, x + 316, 26, CINZA, self.font_pequena, direita=True)

        # Barra de vida
        self.desenhar_barra(
            x + 14, 54, 220, 18,
            personagem.vida, personagem.vida_maxima,
            self.cor_da_vida(personagem),
            self.barras.get(id(personagem))
        )
        self.escrever(f"{personagem.vida}/{personagem.vida_maxima}", x + 316, 54, BRANCO,
                      self.font_pequena, direita=True)

        # Linha de baixo: mana, flechas ou informações extras
        if hasattr(personagem, "mana"):
            self.desenhar_barra(x + 14, 82, 220, 12, personagem.mana, personagem.MANA_MAXIMA, AZUL_MANA)
            self.escrever(f"Mana {personagem.mana}", x + 316, 80, AZUL_MANA, self.font_pequena, direita=True)

        elif hasattr(personagem, "flechas"):
            self.desenhar_barra(x + 14, 82, 220, 12, personagem.flechas, personagem.FLECHAS_MAXIMAS, LARANJA_FLECHA)
            self.escrever(f"Flechas {personagem.flechas}", x + 316, 80, LARANJA_FLECHA, self.font_pequena, direita=True)

        else:
            detalhes = f"Ataque {personagem.ataque}  |  Defesa {personagem.defesa}"
            if isinstance(personagem, ChefeFinalDificil):
                detalhes += f"  |  Poções {len(personagem.inventario)}"
            if getattr(personagem, "congelado", False):
                detalhes += "  |  CONGELADO"
            self.escrever(detalhes, x + 14, 82, CINZA, self.font_pequena, sombra=False)

    def opcoes_do_menu(self):
        # Cada opção: (tecla, nome, detalhe, disponível)
        jogador = self.jogador

        if self.tela == "batalha":
            if isinstance(jogador, Barbaro):
                detalhe = "escolher a arma"
            elif isinstance(jogador, Mago):
                detalhe = "golpe de cajado, recupera mana"
            elif isinstance(jogador, Arqueiro):
                detalhe = "1 flecha comum" if jogador.flechas > 0 else "sem flechas: adaga"
            else:
                detalhe = "golpe de espada"

            opcoes = [
                ("1", "Atacar", detalhe, True),
                ("2", "Usar item", f"{len(jogador.inventario)} itens", len(jogador.inventario) > 0),
                ("3", "Fugir", "abandona a batalha", True),
            ]
            if jogador.nome_habilidade is not None:
                opcoes.append(("4", jogador.nome_habilidade, "abrir lista", jogador.pode_usar_habilidade()))
            return "AÇÕES", opcoes

        if self.tela == "armas":
            opcoes = []
            for i, arma in enumerate(jogador.armas, start=1):
                opcoes.append((str(i), arma.nome, arma.descricao, True))
            opcoes.append(("0", "Voltar", "", True))
            return "ESCOLHA A ARMA", opcoes

        if self.tela == "magias":
            opcoes = []
            for i, magia in enumerate(jogador.magias, start=1):
                detalhe = f"{magia.custo} mana - {magia.descricao}"
                opcoes.append((str(i), magia.nome, detalhe, jogador.pode_lancar(magia)))
            opcoes.append(("0", "Voltar", "", True))
            return "MAGIAS", opcoes

        if self.tela == "flechas":
            opcoes = []
            for i, flecha in enumerate(jogador.tipos_flecha, start=1):
                detalhe = f"gasta {flecha.custo} - {flecha.descricao}"
                opcoes.append((str(i), flecha.nome, detalhe, jogador.pode_disparar(flecha)))
            opcoes.append(("0", "Voltar", "", True))
            return "FLECHAS", opcoes

        if self.tela == "inventario":
            opcoes = []
            for i, item in enumerate(jogador.inventario, start=1):
                opcoes.append((str(i), item.nome, f"recupera {item.valor}", True))
            opcoes.append(("0", "Voltar", "", True))
            return "INVENTÁRIO", opcoes

        # Tela "fim"
        return "FIM DE JOGO", [("S", "Jogar novamente", "", True), ("N", "Sair", "", True)]

    def desenhar_menu(self):
        x, y, largura, altura = 16, 414, 360, 212
        self.desenhar_painel(x, y, largura, altura)

        titulo, opcoes = self.opcoes_do_menu()
        esperando = self.ocupado() and self.tela != "fim"

        if esperando:
            titulo = "AGUARDE..."
        self.escrever(titulo, x + 16, y + 10, DOURADO, self.font)

        linha_y = y + 40
        for tecla, nome, detalhe, disponivel in opcoes:
            ativo = disponivel and not esperando
            cor_caixa = (55, 45, 90) if ativo else (35, 30, 50)
            cor_texto = BRANCO if ativo else CINZA_ESCURO

            pygame.draw.rect(self.screen, cor_caixa, (x + 12, linha_y, largura - 24, 31), border_radius=8)

            # Tecla
            pygame.draw.rect(self.screen, DOURADO if ativo else CINZA_ESCURO,
                             (x + 16, linha_y + 4, 24, 23), border_radius=6)
            self.escrever(tecla, x + 28, linha_y + 7, (25, 20, 35), self.font_pequena, centro=True, sombra=False)

            # Nome e detalhe
            self.escrever(nome, x + 50, linha_y + 3, cor_texto, self.font_pequena, sombra=False)
            if detalhe:
                detalhe = self.quebrar_texto(detalhe, largura - 80, self.font_mini)[0]
                self.escrever(detalhe, x + 50, linha_y + 18, CINZA if ativo else CINZA_ESCURO,
                              self.font_mini, sombra=False)

            linha_y += 34

    def cor_da_mensagem(self, texto):
        if "CRÍTICO" in texto or "DEVASTADOR" in texto:
            return DOURADO
        if "derrotado" in texto or "fugiu" in texto:
            return VERMELHO
        if "recuperou" in texto or "sugando" in texto:
            return VERDE
        if "congel" in texto:
            return (150, 220, 255)
        if " VS " in texto:
            return DOURADO
        return BRANCO

    def desenhar_mensagens(self):
        x, y, largura, altura = 392, 414, 552, 212
        self.desenhar_painel(x, y, largura, altura)
        self.escrever("REGISTRO DA BATALHA", x + 16, y + 10, DOURADO, self.font)

        # Quebra as mensagens em linhas (guardando a cor de cada uma)
        linhas = []
        for mensagem in self.mensagens:
            cor = self.cor_da_mensagem(mensagem)
            for linha in self.quebrar_texto(mensagem, largura - 32, self.font_pequena):
                linhas.append((linha, cor))

        linhas = linhas[-8:]
        linha_y = y + 42
        for i, (linha, cor) in enumerate(linhas):
            # As mais antigas ficam mais apagadas
            if i < len(linhas) - 3:
                cor = tuple(int(c * 0.65) for c in cor)
            self.escrever(linha, x + 16, linha_y, cor, self.font_pequena, sombra=False)
            linha_y += 20

    def desenhar_tela_batalha(self):
        arena = self.arena
        arena.blit(self.fundo_batalha, (0, 0))
        self.desenhar_ambiente(arena)

        self.desenhar_lutador(arena, self.jogador, X_JOGADOR, 1)
        self.desenhar_lutador(arena, self.inimigo, X_INIMIGO, -1)

        # No fim de jogo os efeitos (confetes) são desenhados por cima de tudo
        if self.tela != "fim":
            self.efeitos.desenhar(arena)

        # Tremor da tela
        tremor_x = 0
        tremor_y = 0
        inicio, forca = self.tremor
        passado = self.tempo - inicio
        if 0 <= passado < 0.4:
            amplitude = int(forca * (1 - passado / 0.4))
            tremor_x = random.randint(-amplitude, amplitude)
            tremor_y = random.randint(-amplitude, amplitude)

        self.screen.fill((10, 8, 20))
        self.screen.blit(arena, (tremor_x, tremor_y))

        # Painéis de status
        self.desenhar_status(self.jogador, 16, (130, 200, 255), nome_da_classe(self.jogador))
        self.desenhar_status(self.inimigo, WIDTH - 346, (255, 130, 120), self.dificuldade)

        if self.tela == "fim":
            escuro = pygame.Surface((WIDTH, ARENA_ALTURA), pygame.SRCALPHA)
            escuro.fill((0, 0, 0, 120))
            self.screen.blit(escuro, (0, 0))

            cor = DOURADO if self.resultado == "VITÓRIA!" else (240, 90, 90)
            pulso = 1 + 0.04 * math.sin(self.tempo * 4)
            imagem = self.font_titulo.render(self.resultado, True, cor)
            imagem = pygame.transform.smoothscale_by(imagem, pulso * 1.3)
            contorno = self.font_titulo.render(self.resultado, True, (30, 10, 30))
            contorno = pygame.transform.smoothscale_by(contorno, pulso * 1.3)

            x = WIDTH // 2 - imagem.get_width() // 2
            y = 180 - imagem.get_height() // 2
            for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (4, 5)):
                self.screen.blit(contorno, (x + dx, y + dy))
            self.screen.blit(imagem, (x, y))

            # Confetes por cima de tudo
            self.efeitos.desenhar(self.screen)

        self.desenhar_menu()
        self.desenhar_mensagens()

    # --------------------------------------------------------
    # DESENHO PRINCIPAL
    # --------------------------------------------------------

    def draw(self):
        if self.tela == "classe":
            self.desenhar_tela_classe()
        elif self.tela == "tipo_mago":
            self.desenhar_tela_tipo_mago()
        elif self.tela == "nome":
            self.desenhar_tela_nome()
        elif self.tela == "inimigo":
            self.desenhar_tela_inimigo()
        else:
            self.desenhar_tela_batalha()

        pygame.display.flip()

    # --------------------------------------------------------
    # LOOP PRINCIPAL
    # --------------------------------------------------------

    def run(self):

        while self.running:

            # Tempo do quadro em segundos
            dt = self.clock.tick(FPS) / 1000
            self.tempo += dt

            # 1. Eventos
            self.handle_events()

            # 2. Atualização (efeitos, turnos agendados)
            self.update(dt)

            # 3. Desenho
            self.draw()

        pygame.quit()


def clarear(cor):
    return tuple(int(c + (255 - c) * 0.35) for c in cor[:3])


# ============================================================
# INÍCIO DO PROGRAMA
# ============================================================

if __name__ == "__main__":

    game = Game()

    game.run()
