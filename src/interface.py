import contextlib
import io
import math
import random

import pygame

from guerreiro import Guerreiro
from barbaro import Barbaro
from paladino import Paladino
from assassina import Assassina
from mago import Mago
from magos import MagoElemental, MagoFogo, MagoGelo, MagoRaio
from arqueiro import Arqueiro
from arqueiro_flechas import ArqueiroFlechas
from vampiro import Vampiro
from chefe_final import ChefeFinal
from chefe_dificil import ChefeFinalDificil
from inimigos_novos import Esqueleto, Bruxa, AranhaGigante, Golem
from item import PocaoVida, PocaoMana, Aljava
from estados import sofrer_veneno, esta_envenenado, esta_paralisado
from main import INIMIGOS
from desenhos import criar_desenho, QUADROS
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

# Investida (correr até o inimigo, bater e voltar)
DISTANCIA_INVESTIDA = 350
TEMPO_IDA = 0.18
TEMPO_PARADO = 0.12
TEMPO_VOLTA = 0.25

# Espera depois de cada golpe antes do próximo turno
PAUSA_ENTRE_TURNOS = 0.35

# Cores
BRANCO = (255, 255, 255)
CINZA = (160, 155, 185)
CINZA_ESCURO = (90, 85, 115)
DOURADO = (255, 210, 80)
VERMELHO = (240, 70, 70)
VERDE = (90, 220, 110)
VERDE_VENENO = (170, 255, 110)
AZUL_MANA = (70, 140, 255)
LARANJA_FLECHA = (230, 150, 60)
ROXO_ENERGIA = (180, 110, 255)
FUNDO_PAINEL = (22, 18, 40, 225)
BORDA_PAINEL = (120, 100, 190)

# Tecla -> (nome, classe, cor, descrição, nome padrão)
CLASSES = {
    "1": ("Guerreiro", Guerreiro, (90, 150, 255), "Equilibrado e com muita defesa.", "Arthur"),
    "2": ("Bárbaro", Barbaro, (240, 130, 60), "Escolhe a arma a cada ataque.", "Bjorn"),
    "3": ("Paladino", Paladino, (255, 210, 90), "Orações: cura, golpe sagrado e escudo.", "Galahad"),
    "4": ("Mago", Mago, (180, 100, 255), "Escolhe o elemento e lança magias.", "Merlin"),
    "5": ("Arqueira", ArqueiroFlechas, (90, 210, 120), "Escolhe o tipo de flecha.", "Lyra"),
    "6": ("Assassina", Assassina, (200, 110, 255), "Críticos, veneno e esquiva.", "Nyx"),
}
TECLA_MAGO = "4"

# Tecla -> (classe, cor)
TIPOS_MAGO = {
    "1": (MagoFogo, (255, 120, 50)),
    "2": (MagoGelo, (120, 210, 255)),
    "3": (MagoRaio, (255, 225, 70)),
}

# Inimigos em ordem de dificuldade (os do main.py e os novos)
INIMIGOS_JOGO = {
    "1": ("fácil", INIMIGOS["1"][1]),
    "2": ("fácil", lambda: Esqueleto()),
    "3": ("médio", INIMIGOS["2"][1]),
    "4": ("médio", lambda: Bruxa()),
    "5": ("difícil", INIMIGOS["3"][1]),
    "6": ("difícil", INIMIGOS["4"][1]),
    "7": ("difícil", lambda: AranhaGigante()),
    "8": ("muito difícil", lambda: Golem()),
    "9": ("CHEFE FINAL", lambda: ChefeFinalDificil()),
}

CORES_INIMIGO = {
    "1": (90, 210, 100),
    "2": (150, 230, 200),
    "3": (240, 200, 60),
    "4": (140, 220, 110),
    "5": (255, 130, 50),
    "6": (230, 60, 80),
    "7": (170, 120, 200),
    "8": (110, 200, 255),
    "9": (180, 90, 255),
}

DESCRICAO_INIMIGO = {
    "1": "Fraco, bom para começar.",
    "2": "Se levanta uma vez ao morrer.",
    "3": "Forte e resistente.",
    "4": "Maldição a cada 2 ataques.",
    "5": "Ataque muito alto.",
    "6": "Suga a vida a cada mordida.",
    "7": "Envenena e paralisa.",
    "8": "Carrega e esmaga com 2x.",
    "9": "Crítico, cura e golpe devastador.",
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def criar_jogador(classe, tipo_mago, nome):
    nome_classe, Classe, cor, descricao, nome_padrao = CLASSES[classe]

    if classe == TECLA_MAGO:
        Classe = TIPOS_MAGO[tipo_mago][0]

    jogador = Classe(nome or nome_padrao)

    # Itens iniciais (mesmas regras do main.py)
    if isinstance(jogador, Mago):
        jogador.adicionar_item(PocaoMana())
    if isinstance(jogador, Arqueiro):
        jogador.adicionar_item(Aljava())
    jogador.adicionar_item(PocaoVida())
    jogador.adicionar_item(PocaoVida())
    return jogador


def nome_da_classe(personagem):
    if isinstance(personagem, Barbaro):
        return "Bárbaro"
    if isinstance(personagem, Guerreiro):
        return "Guerreiro"
    if isinstance(personagem, Paladino):
        return "Paladino"
    if isinstance(personagem, Assassina):
        return "Assassina"
    if isinstance(personagem, MagoElemental):
        return f"Mago de {personagem.elemento}"
    if isinstance(personagem, Mago):
        return "Mago"
    if isinstance(personagem, Arqueiro):
        return "Arqueira"
    return ""


def habilidades_do(jogador):
    """Devolve (título, lista, função "pode usar?", função "usar", tipo do efeito)."""
    if isinstance(jogador, MagoElemental):
        return "MAGIAS", jogador.magias, jogador.pode_lancar, jogador.lancar_magia, "magia"
    if isinstance(jogador, ArqueiroFlechas):
        return "FLECHAS", jogador.tipos_flecha, jogador.pode_disparar, jogador.disparar, "flecha"
    if isinstance(jogador, Paladino):
        return "ORAÇÕES", jogador.oracoes, jogador.pode_orar, jogador.orar, "oracao"
    if isinstance(jogador, Assassina):
        return "TÉCNICAS", jogador.tecnicas, jogador.pode_usar_tecnica, jogador.usar_tecnica, "tecnica"
    return None


def texto_do_custo(jogador, habilidade):
    if isinstance(jogador, MagoElemental):
        return f"{habilidade.custo} mana"
    if isinstance(jogador, ArqueiroFlechas):
        return f"gasta {habilidade.custo}"
    if isinstance(jogador, Paladino):
        return f"{habilidade.custo} fé"
    return f"{habilidade.custo} energia"


def recurso_do(personagem):
    """Recurso extra do personagem: (nome, atual, máximo, cor) ou None."""
    if hasattr(personagem, "mana"):
        return "Mana", personagem.mana, personagem.MANA_MAXIMA, AZUL_MANA
    if hasattr(personagem, "flechas"):
        return "Flechas", personagem.flechas, personagem.FLECHAS_MAXIMAS, LARANJA_FLECHA
    if hasattr(personagem, "energia"):
        return "Energia", personagem.energia, personagem.ENERGIA_MAXIMA, ROXO_ENERGIA
    if hasattr(personagem, "fe"):
        return "Fé", personagem.fe, personagem.FE_MAXIMA, DOURADO
    return None


def suave(p):
    # Curva de movimento: começa e termina devagar
    return p * p * (3 - 2 * p)


def clarear(cor):
    return tuple(int(c + (255 - c) * 0.35) for c in cor[:3])


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
        self.font_media = pygame.font.Font(None, 34)
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
        # "armas", "habilidades", "inventario" e "fim"
        self.trocar_tela("classe")
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
        self.investidas = {}            # id do personagem -> (início, distância)
        self.atingidos = {}             # id do personagem -> (início, força)
        self.tremor = (0, 0)            # (início, força)

        # Valor "atrasado" das barras de vida (efeito de barra descendo)
        self.barras = {}

    def trocar_tela(self, nova_tela):
        # Troca de tela com um escurecimento rápido
        self.tela = nova_tela
        self.inicio_transicao = self.tempo

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
        # Enquanto houver algo agendado, o jogador espera
        return self.pendente is not None

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

                elif self.tela == "habilidades":
                    self.escolher_habilidade(event)

                elif self.tela == "inventario":
                    self.escolher_item(event)

    def escolher_classe(self, event):
        if event.unicode in CLASSES:
            self.classe = event.unicode

            if self.classe == TECLA_MAGO:
                self.trocar_tela("tipo_mago")
            else:
                self.trocar_tela("nome")

    def escolher_tipo_mago(self, event):
        if event.unicode in TIPOS_MAGO:
            self.tipo_mago = event.unicode
            self.trocar_tela("nome")

    def digitar_nome(self, event):
        if event.key == pygame.K_RETURN:
            self.jogador = criar_jogador(self.classe, self.tipo_mago, self.nome.strip())
            self.trocar_tela("inimigo")

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
            self.trocar_tela("batalha")

    def escolher_acao(self, event):
        tecla = event.unicode
        jogador = self.jogador

        if tecla == "1":
            if isinstance(jogador, Barbaro):
                self.tela = "armas"
            else:
                # A arqueira sem flechas ataca com a adaga
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
            self.trocar_tela("fim")

        elif tecla == "4" and habilidades_do(jogador) is not None:
            if jogador.pode_usar_habilidade():
                self.tela = "habilidades"
            else:
                self.adicionar_mensagem(jogador.mensagem_sem_recurso)

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

    def escolher_habilidade(self, event):
        if event.unicode == "0":
            self.tela = "batalha"
            return

        titulo, lista, pode_usar, usar, tipo = habilidades_do(self.jogador)
        posicao = self.numero_escolhido(event, lista)

        if posicao is not None:
            habilidade = lista[posicao]

            if pode_usar(habilidade):
                self.jogada(usar, habilidade, self.inimigo, efeito=(tipo, habilidade.nome))
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
        espera = impacto + PAUSA_ENTRE_TURNOS

        if not self.inimigo.esta_vivo():
            self.agendar(espera + 0.4, self.vitoria)
        elif not self.jogador.esta_vivo():
            self.agendar(espera + 0.4, self.derrota)
        else:
            self.agendar(espera, self.turno_do_inimigo)

    def sofrer_veneno_agora(self, personagem):
        # Aplica o veneno do começo do turno, com efeito e número
        vidas = self.guardar_vidas()
        self.executar(sofrer_veneno, personagem)
        x, y = self.centro(personagem)
        self.efeitos.adicionar(efeitos.Explosao(x, y, efeitos.VENENO, 20, 30, gravidade=-120))
        self.atingir(personagem, 0, 10)
        self.mostrar_numeros(vidas, 0.05)

    def turno_do_inimigo(self):
        inimigo = self.inimigo
        jogador = self.jogador

        # 1. Veneno no inimigo
        if esta_envenenado(inimigo):
            self.sofrer_veneno_agora(inimigo)
            if not inimigo.esta_vivo():
                self.agendar(0.9, self.vitoria)
                return

        vidas = self.guardar_vidas()
        esquivando_antes = getattr(jogador, "esquivando", False)
        escudo_antes = getattr(jogador, "escudo_de_luz", False)

        # 2. Congelado perde o ataque; senão, ataca
        if getattr(inimigo, "congelado", False):
            inimigo.congelado = False
            self.adicionar_mensagem(f"{inimigo.nome} está congelado e perdeu o ataque!")
            self.efeitos.adicionar(efeitos.Cristais(X_INIMIGO, CHAO_Y))
            impacto = 0.1
        else:
            self.executar(inimigo.atacar, jogador)
            impacto = self.efeito_do_inimigo()

        # 3. Esquiva e Escudo de Luz que foram usados agora
        x, y = self.centro(jogador)
        if esquivando_antes and not jogador.esquivando:
            self.efeitos.adicionar(efeitos.TextoFlutuante("ESQUIVOU!", x, y - 40, ROXO_ENERGIA, self.font_media, impacto))
        if escudo_antes and not jogador.escudo_de_luz:
            self.efeitos.adicionar(efeitos.Onda(x, y, (255, 225, 120), 110, atraso=impacto))
            self.efeitos.adicionar(efeitos.TextoFlutuante("BLOQUEOU!", x, y + 60, DOURADO, self.font_media, impacto))

        self.mostrar_numeros(vidas, impacto)

        if not jogador.esta_vivo():
            self.agendar(impacto + 0.8, self.derrota)
        else:
            self.agendar(impacto + PAUSA_ENTRE_TURNOS, self.inicio_turno_jogador)

    def inicio_turno_jogador(self):
        jogador = self.jogador

        # Veneno no herói
        if esta_envenenado(jogador):
            self.sofrer_veneno_agora(jogador)
            if not jogador.esta_vivo():
                self.agendar(0.9, self.derrota)
                return

        # Paralisado: perde a vez e o inimigo ataca de novo
        if esta_paralisado(jogador):
            jogador.paralisado = False
            self.adicionar_mensagem(f"{jogador.nome} está paralisado e perdeu a vez!")
            x, y = self.centro(jogador)
            self.efeitos.adicionar(efeitos.TextoFlutuante("PARALISADO!", x, y - 40, (220, 220, 255), self.font_media))
            self.agendar(0.9, self.turno_do_inimigo)

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
    # POSIÇÕES E ANIMAÇÕES
    # --------------------------------------------------------

    def x_do(self, personagem):
        if personagem is self.jogador:
            return X_JOGADOR
        return X_INIMIGO

    def direcao_do(self, personagem):
        # 1 = olha para a direita (herói), -1 = para a esquerda (inimigo)
        return 1 if personagem is self.jogador else -1

    def centro(self, personagem):
        return (self.x_do(personagem), CHAO_Y - 120)

    def ponta(self, personagem):
        # De onde saem magias e flechas
        return (self.x_do(personagem) + 70 * self.direcao_do(personagem), CHAO_Y - 150)

    def investir(self, personagem, distancia=DISTANCIA_INVESTIDA):
        # Corre até o alvo e volta. Devolve o tempo até o golpe acertar.
        self.investidas[id(personagem)] = (self.tempo, distancia)
        return TEMPO_IDA

    def passo_a_frente(self, personagem):
        # Pequeno passo ao lançar magia ou atirar
        self.investir(personagem, 30)

    def atingir(self, personagem, atraso=0.0, forca=25):
        self.atingidos[id(personagem)] = (self.tempo + atraso, forca)

    def tremer(self, forca, atraso=0.0):
        self.tremor = (self.tempo + atraso, forca)

    def deslocamento(self, personagem):
        """Quanto o personagem está deslocado agora (investida e empurrão)."""
        direcao = self.direcao_do(personagem)
        dx = 0

        # Investida
        dados = self.investidas.get(id(personagem))
        if dados is not None:
            inicio, distancia = dados
            t = self.tempo - inicio
            if 0 <= t < TEMPO_IDA:
                dx += distancia * suave(t / TEMPO_IDA) * direcao
            elif t < TEMPO_IDA + TEMPO_PARADO:
                dx += distancia * direcao
            elif t < TEMPO_IDA + TEMPO_PARADO + TEMPO_VOLTA:
                volta = (t - TEMPO_IDA - TEMPO_PARADO) / TEMPO_VOLTA
                dx += distancia * (1 - suave(volta)) * direcao

        # Empurrão para trás quando é atingido
        dados = self.atingidos.get(id(personagem))
        if dados is not None:
            inicio, forca = dados
            t = self.tempo - inicio
            if 0 <= t < 0.35:
                dx -= forca * (1 - t / 0.35) * direcao

        return dx

    def foi_atingido_agora(self, personagem):
        dados = self.atingidos.get(id(personagem))
        if dados is None:
            return False
        return 0 <= self.tempo - dados[0] < 0.15

    def quadro_animacao(self, deslocamento=0):
        # Troca o quadro 8 vezes por segundo
        return int(self.tempo * 8 + deslocamento) % QUADROS

    # --------------------------------------------------------
    # NÚMEROS E EFEITOS
    # --------------------------------------------------------

    def mostrar_numeros(self, vidas, atraso):
        # Mostra "-dano" ou "+cura" em cima de quem mudou de vida
        for personagem, vida_antes in vidas:
            x, y = self.centro(personagem)

            # O esqueleto que acabou de se levantar
            if getattr(personagem, "renascendo", False):
                personagem.renascendo = False
                self.efeitos.adicionar(efeitos.Onda(x, y, (120, 255, 190), 120, atraso=atraso + 0.2))
                self.efeitos.adicionar(efeitos.Explosao(x, y, efeitos.OSSOS, 30, 40, atraso=atraso + 0.2, gravidade=-80))
                self.efeitos.adicionar(efeitos.TextoFlutuante("RENASCEU!", x, y - 70, (120, 255, 190),
                                                              self.font_dano, atraso + 0.2))
                continue

            diferenca = personagem.vida - vida_antes
            if diferenca < 0:
                self.efeitos.adicionar(efeitos.TextoFlutuante(str(diferenca), x, y - 70, VERMELHO, self.font_dano, atraso))
            elif diferenca > 0:
                self.efeitos.adicionar(efeitos.TextoFlutuante(f"+{diferenca}", x, y - 70, VERDE, self.font_dano, atraso))

    def texto(self, texto, personagem, cor, atraso=0.0):
        x, y = self.centro(personagem)
        self.efeitos.adicionar(efeitos.TextoFlutuante(texto, x, y + 20, cor, self.font_media, atraso))

    def efeito_do_jogador(self, tipo, nome=""):
        """Cria o efeito visual da ação do jogador e devolve o tempo até o impacto."""
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

        if tipo == "atacar":
            impacto = self.efeito_de_ataque(nome, origem, x, y)
        elif tipo == "arma":
            impacto = self.efeito_de_arma(nome, x, y)
        elif tipo == "magia":
            self.passo_a_frente(jogador)
            impacto = self.efeito_de_magia(nome, origem, x, y)
        elif tipo == "flecha":
            impacto = self.efeito_de_flecha(nome, origem, x, y)
        elif tipo == "oracao":
            impacto = self.efeito_de_oracao(nome, x, y)
        else:
            impacto = self.efeito_de_tecnica(nome, x, y)

        # Orações e técnicas de defesa não acertam o inimigo
        if nome not in ("Cura Sagrada", "Escudo de Luz", "Esquiva"):
            self.atingir(self.inimigo, impacto)
        return impacto

    def efeito_de_ataque(self, nome, origem, x, y):
        jogador = self.jogador
        adicionar = self.efeitos.adicionar
        E = efeitos

        if isinstance(jogador, Mago):
            self.passo_a_frente(jogador)
            bola = E.Projetil(origem, (x, y), (200, 130, 255), "bola", 7, 0.3, rastro=E.ROXO)
            bola.proximos = [E.Explosao(x, y, E.ROXO, 15, 30)]
            adicionar(bola)
            return 0.3

        if isinstance(jogador, Arqueiro) and nome == "normal":
            flecha = E.Projetil(origem, (x, y), (220, 60, 60), "flecha", 6, 0.3, rastro=E.MADEIRA)
            flecha.proximos = [E.Explosao(x, y, E.MADEIRA, 8, 20)]
            adicionar(flecha)
            return 0.3

        impacto = self.investir(jogador)

        if isinstance(jogador, Paladino):
            adicionar(E.Corte(x, y, (255, 220, 120), 70, atraso=impacto))
            adicionar(E.Onda(x, y, (255, 230, 150), 70, atraso=impacto))
        elif isinstance(jogador, Assassina):
            adicionar(E.Corte(x, y, (190, 120, 255), 65, atraso=impacto, quantidade=2))
            if jogador.ultimo_critico:
                adicionar(E.FlashTela((255, 255, 255), 0.25, atraso=impacto, transparencia=130))
                adicionar(E.TextoFlutuante("CRÍTICO!", x, y + 20, DOURADO, self.font_media, impacto))
                self.tremer(10, impacto)
        else:
            adicionar(E.Corte(x, y, (170, 200, 255), 70, atraso=impacto))
        return impacto

    def efeito_de_arma(self, nome, x, y):
        adicionar = self.efeitos.adicionar
        E = efeitos
        impacto = self.investir(self.jogador)

        if nome == "Espada":
            adicionar(E.Corte(x, y, (190, 210, 255), 70, atraso=impacto))
        elif nome == "Machado":
            adicionar(E.Corte(x, y, (255, 150, 60), 95, atraso=impacto, quantidade=2))
            adicionar(E.Explosao(x, y, E.FOGO, 20, 35, atraso=impacto))
            self.tremer(8, impacto)
        elif nome == "Martelo":
            adicionar(E.Onda(x, CHAO_Y, (230, 220, 200), 150, atraso=impacto, achatada=True))
            adicionar(E.Explosao(x, y + 40, E.PEDRA, 30, 40, atraso=impacto))
            self.tremer(13, impacto)
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
        self.passo_a_frente(self.jogador)

        if nome == "Flecha de fogo":
            flecha = E.Projetil(origem, (x, y), (255, 120, 40), "flecha", 7, 0.3, rastro=E.FOGO)
            flecha.proximos = [E.Explosao(x, y, E.FOGO, 30, 40)]
            adicionar(flecha)
            return 0.3

        if nome == "Flecha perfurante":
            flecha = E.Projetil(origem, (x, y), (120, 230, 255), "flecha", 6, 0.18,
                                rastro=[(150, 240, 255), (255, 255, 255)])
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

    def efeito_de_oracao(self, nome, x, y):
        adicionar = self.efeitos.adicionar
        E = efeitos
        px, py = self.centro(self.jogador)

        if nome == "Cura Sagrada":
            adicionar(E.Raio(px, py + 80, cor=(255, 230, 140)))
            adicionar(E.Cura(px, py, E.LUZ))
            return 0.15

        if nome == "Escudo de Luz":
            adicionar(E.Onda(px, py, (255, 225, 120), 110))
            adicionar(E.Cura(px, py, E.LUZ))
            return 0.1

        # Golpe Sagrado
        impacto = self.investir(self.jogador)
        adicionar(E.Raio(x, y, atraso=impacto, cor=(255, 230, 140)))
        adicionar(E.Explosao(x, y, E.LUZ, 45, 55, atraso=impacto))
        adicionar(E.FlashTela((255, 240, 180), 0.3, atraso=impacto, transparencia=120))
        self.tremer(10, impacto)
        return impacto

    def efeito_de_tecnica(self, nome, x, y):
        adicionar = self.efeitos.adicionar
        E = efeitos
        px, py = self.centro(self.jogador)

        if nome == "Esquiva":
            adicionar(E.Explosao(px, py, E.SOMBRA, 35, 40, gravidade=-80))
            return 0.1

        if nome == "Veneno":
            impacto = self.investir(self.jogador)
            adicionar(E.Corte(x, y, (120, 230, 80), 65, atraso=impacto, quantidade=2))
            adicionar(E.Explosao(x, y, E.VENENO, 30, 40, atraso=impacto, gravidade=-60))
            return impacto

        # Golpe nas Sombras
        adicionar(E.Explosao(px, py, E.SOMBRA, 30, 35, gravidade=-80))
        impacto = self.investir(self.jogador)
        adicionar(E.Corte(x, y, (90, 40, 140), 110, atraso=impacto))
        adicionar(E.Explosao(x, y, E.SOMBRA, 40, 50, atraso=impacto))
        adicionar(E.FlashTela((40, 10, 60), 0.3, atraso=impacto, transparencia=150))
        self.tremer(12, impacto)
        return impacto

    def efeito_do_inimigo(self):
        """Cria o efeito visual do ataque do inimigo e devolve o tempo até o impacto."""
        inimigo = self.inimigo
        x, y = self.centro(self.jogador)
        adicionar = self.efeitos.adicionar
        E = efeitos
        acao = getattr(inimigo, "ultima_acao", "ataque")
        ix, iy = self.centro(inimigo)
        origem = self.ponta(inimigo)

        # Ações que não acertam o herói
        if acao == "cura":
            adicionar(E.Cura(ix, iy, E.CURA))
            return 0.1

        if acao == "carregar":
            adicionar(E.Cura(ix, iy, [(255, 200, 120), (255, 150, 40), (220, 100, 20)]))
            self.texto("CARREGANDO...", inimigo, (255, 170, 70))
            return 0.1

        if isinstance(inimigo, ChefeFinal):
            # O lich ataca com magia de fogo azul
            self.passo_a_frente(inimigo)
            azul = [(230, 250, 255), (110, 190, 255), (40, 90, 255)]

            if acao == "devastador":
                for i in range(3):
                    adicionar(E.Raio(x + (i - 1) * 30, y, atraso=i * 0.15, cor=(130, 170, 255)))
                adicionar(E.Onda(x, CHAO_Y, (190, 100, 255), 180, atraso=0.15, achatada=True))
                adicionar(E.TextoFlutuante("DEVASTADOR!", x, y + 20, (200, 130, 255), self.font_media, 0.15))
                self.tremer(12, 0.15)
                impacto = 0.15
            else:
                tamanho = 18 if acao == "critico" else 12
                bola = E.Projetil(origem, (x, y), (110, 170, 255), "bola", tamanho, 0.35, rastro=azul)
                bola.proximos = [E.Explosao(x, y, azul, 35, 45)]
                adicionar(bola)
                impacto = 0.35

            if acao == "critico":
                adicionar(E.FlashTela((255, 255, 255), 0.3, atraso=impacto, transparencia=170))
                adicionar(E.TextoFlutuante("CRÍTICO!", x, y + 20, DOURADO, self.font_media, impacto))
                self.tremer(16, impacto)

        elif isinstance(inimigo, Bruxa):
            self.passo_a_frente(inimigo)
            if acao == "maldicao":
                bola = E.Projetil(origem, (x, y), (180, 80, 230), "bola", 14, 0.4, rastro=E.ROXO, altura_arco=40)
                bola.proximos = [E.Explosao(x, y, E.ROXO, 35, 45)]
                adicionar(E.TextoFlutuante("MALDIÇÃO!", x, y + 20, (200, 130, 255), self.font_media, 0.4))
            else:
                bola = E.Projetil(origem, (x, y), (110, 200, 80), "bola", 9, 0.35, rastro=E.VENENO)
                bola.proximos = [E.Explosao(x, y, E.VENENO, 20, 30)]
            adicionar(bola)
            impacto = bola.duracao

        elif inimigo.nome == "Dragão Jovem":
            self.passo_a_frente(inimigo)
            impacto = 0.35
            bafo = E.Projetil(origem, (x, y), (255, 120, 30), "bola", 16, impacto, rastro=E.FOGO)
            bafo.proximos = [E.Explosao(x, y, E.FOGO, 35, 45)]
            adicionar(bafo)

        elif isinstance(inimigo, AranhaGigante) and inimigo.paralisou:
            # Lança a teia de longe
            self.passo_a_frente(inimigo)
            impacto = 0.35
            teia = E.Projetil(origem, (x, y), (240, 240, 250), "teia", 22, impacto, rastro=[(230, 230, 240)])
            teia.proximos = [E.Explosao(x, y, [(255, 255, 255), (210, 210, 230)], 25, 35)]
            adicionar(teia)
            adicionar(E.TextoFlutuante("PARALISADO!", x, y - 20, (220, 220, 255), self.font_media, impacto))

        else:
            # Ataques corpo a corpo: correm até o herói
            impacto = self.investir(inimigo)

            if isinstance(inimigo, Golem):
                adicionar(E.Onda(x, CHAO_Y, (220, 200, 170), 170, atraso=impacto, achatada=True))
                adicionar(E.Explosao(x, y + 30, E.PEDRA, 40, 50, atraso=impacto))
                adicionar(E.TextoFlutuante("ESMAGAR!", x, y + 20, (255, 170, 70), self.font_media, impacto))
                self.tremer(16, impacto)
            elif isinstance(inimigo, Vampiro):
                adicionar(E.Corte(x, y, (220, 30, 50), 60, atraso=impacto, quantidade=2))
                adicionar(E.Dreno((x, y), (ix - DISTANCIA_INVESTIDA, iy), E.SANGUE, atraso=impacto))
            elif isinstance(inimigo, Esqueleto):
                adicionar(E.Corte(x, y, (230, 225, 200), 65, atraso=impacto))
            elif isinstance(inimigo, AranhaGigante):
                adicionar(E.Corte(x, y, (120, 230, 80), 60, atraso=impacto, quantidade=2))
            else:
                adicionar(E.Corte(x, y, (255, 110, 70), 65, atraso=impacto))

        # Veneno da aranha
        if isinstance(inimigo, AranhaGigante) and inimigo.envenenou:
            adicionar(E.Explosao(x, y, E.VENENO, 30, 40, atraso=impacto, gravidade=-60))
            adicionar(E.TextoFlutuante("ENVENENADO!", x, y + 50, VERDE_VENENO, self.font_media, impacto + 0.1))

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
        pygame.draw.circle(self.screen, cor, (x + 22, y + 28), 14)
        pygame.draw.circle(self.screen, BRANCO, (x + 22, y + 28), 14, 2)
        self.escrever(tecla, x + 22, y + 19, (20, 15, 30), self.font, centro=True, sombra=False)

    def desenhar_barra(self, x, y, largura, altura, atual, maximo, cor, atrasado=None):
        pygame.draw.rect(self.screen, (40, 35, 55), (x, y, largura, altura), border_radius=altura // 2)

        # Parte "atrasada" clara (mostra o dano que acabou de entrar)
        if atrasado is not None and atrasado > atual:
            parte = int(largura * min(atrasado, maximo) / maximo)
            pygame.draw.rect(self.screen, (255, 240, 200), (x, y, parte, altura), border_radius=altura // 2)

        cheia = int(largura * max(0, min(atual, maximo)) / maximo)
        if cheia > 0:
            pygame.draw.rect(self.screen, cor, (x, y, cheia, altura), border_radius=altura // 2)
            pygame.draw.rect(self.screen, clarear(cor), (x + 3, y + 2, max(0, cheia - 6), altura // 3),
                             border_radius=altura // 2)

        pygame.draw.rect(self.screen, (15, 10, 25), (x, y, largura, altura), 2, border_radius=altura // 2)

    def desenhar_atributo(self, x, y, largura, rotulo, valor, maximo, cor):
        self.escrever(rotulo, x, y, CINZA, self.font_mini, sombra=False)
        self.escrever(str(valor), x + largura, y, BRANCO, self.font_mini, direita=True, sombra=False)
        self.desenhar_barra(x, y + 15, largura, 7, valor, maximo, cor)

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

    def balanco(self, x, amplitude=3):
        # Pequeno movimento de "respiração"
        return math.sin(self.tempo * 2.5 + x) * amplitude

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

        x = 16
        for indice, (tecla, (nome, Classe, cor, descricao, nome_padrao)) in enumerate(CLASSES.items()):
            personagem = Classe(nome)

            self.desenhar_cartao(x, 120, 148, 450, cor, tecla)

            desenho = criar_desenho(personagem, escala=0.85, quadro=self.quadro_animacao(indice * 2))
            self.screen.blit(desenho, (x + 6, 135 + self.balanco(x)))

            centro = x + 74
            self.escrever(nome, centro, 312, cor, self.font, centro=True)

            self.desenhar_atributo(x + 14, 342, 120, "Vida", personagem.vida, 140, (70, 210, 90))
            self.desenhar_atributo(x + 14, 372, 120, "Ataque", personagem.ataque, 30, (240, 90, 70))
            self.desenhar_atributo(x + 14, 402, 120, "Defesa", personagem.defesa, 15, (90, 150, 255))

            recurso = recurso_do(personagem)
            if recurso is not None:
                self.escrever(f"{recurso[0]}: {recurso[2]}", centro, 436, recurso[3], self.font_pequena, centro=True)

            y = 465
            for linha in self.quebrar_texto(descricao, 130, self.font_mini):
                self.escrever(linha, centro, y, BRANCO, self.font_mini, centro=True)
                y += 17

            x += 156

        self.escrever("Pressione de 1 a 6", WIDTH // 2, 592, DOURADO, self.font, centro=True)

    # --------------------------------------------------------
    # TELA: TIPO DE MAGO
    # --------------------------------------------------------

    def desenhar_tela_tipo_mago(self):
        self.desenhar_fundo_menu()
        self.escrever_titulo("Escolha seu elemento", 22)

        x = 40
        for indice, (tecla, (ClasseMago, cor)) in enumerate(TIPOS_MAGO.items()):
            mago = ClasseMago("Mago")

            self.desenhar_cartao(x, 110, 280, 470, cor, tecla)

            desenho = criar_desenho(mago, quadro=self.quadro_animacao(indice * 3))
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

        nome, Classe, cor, descricao, nome_padrao = CLASSES[self.classe]
        if self.classe == TECLA_MAGO:
            Classe, cor = TIPOS_MAGO[self.tipo_mago]
            personagem = Classe("Mago")
            rotulo = f"Mago de {personagem.elemento}"
        else:
            personagem = Classe(nome)
            rotulo = nome

        self.desenhar_painel(80, 140, 280, 400, cor)
        desenho = criar_desenho(personagem, escala=1.4, quadro=self.quadro_animacao())
        self.screen.blit(desenho, (108, 160 + self.balanco(0)))
        self.escrever(rotulo, 220, 470, cor, self.font_media, centro=True)

        self.desenhar_painel(420, 260, 460, 80, cor)
        cursor = "|" if int(self.tempo * 2) % 2 == 0 else ""
        self.escrever(self.nome + cursor, 445, 280, BRANCO, self.font_titulo)

        self.escrever("ENTER para confirmar", 420, 370, DOURADO, self.font)
        self.escrever(f"(vazio usa o nome padrão: {nome_padrao})", 420, 400, CINZA, self.font_pequena)

    # --------------------------------------------------------
    # TELA: ESCOLHA DO INIMIGO
    # --------------------------------------------------------

    def desenhar_tela_inimigo(self):
        self.desenhar_fundo_menu()
        self.escrever_titulo("Escolha seu adversário", 14)

        for indice, (tecla, (dificuldade, fabrica)) in enumerate(INIMIGOS_JOGO.items()):
            inimigo = fabrica()
            cor = CORES_INIMIGO[tecla]

            # 5 cartões na primeira linha e 4 na segunda
            if indice < 5:
                x = 10 + indice * 190
                y = 86
            else:
                x = 105 + (indice - 5) * 190
                y = 330

            self.desenhar_cartao(x, y, 180, 230, cor, tecla)

            desenho = criar_desenho(inimigo, escala=0.62, quadro=self.quadro_animacao(indice))
            desenho = pygame.transform.flip(desenho, True, False)
            self.screen.blit(desenho, (x + 41, y + 8 + self.balanco(x, 2)))

            centro = x + 90
            self.escrever(inimigo.nome, centro, y + 134, cor, self.font, centro=True)
            self.escrever(dificuldade, centro, y + 156, CINZA, self.font_mini, centro=True)

            linha_y = y + 174
            for linha in self.quebrar_texto(DESCRICAO_INIMIGO[tecla], 165, self.font_mini)[:2]:
                self.escrever(linha, centro, linha_y, BRANCO, self.font_mini, centro=True, sombra=False)
                linha_y += 15

            atributos = f"Vida {inimigo.vida}  Atq {inimigo.ataque}  Def {inimigo.defesa}"
            self.escrever(atributos, centro, y + 208, DOURADO, self.font_mini, centro=True, sombra=False)

        self.escrever("Pressione de 1 a 9", WIDTH // 2, 596, DOURADO, self.font, centro=True)

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

    def extra_do_desenho(self, personagem):
        if isinstance(personagem, Barbaro):
            return self.arma_barbaro
        if isinstance(personagem, Golem) and personagem.carregado:
            return "carregando"
        return None

    def desenhar_lutador(self, tela, personagem, x, direcao):
        deslocamento_quadro = 0 if direcao > 0 else 4
        desenho = criar_desenho(personagem, self.extra_do_desenho(personagem), ESCALA_LUTADOR,
                                self.quadro_animacao(deslocamento_quadro))

        if direcao < 0:
            desenho = pygame.transform.flip(desenho, True, False)

        dx = self.deslocamento(personagem)

        # O Lorde Sombrio flutua
        flutua = isinstance(personagem, ChefeFinal)
        if flutua:
            dy = -16 + self.balanco(x, 7)
        else:
            dy = self.balanco(x)

        # Piscar ao ser atingido
        if self.foi_atingido_agora(personagem):
            desenho = desenho.copy()
            desenho.fill((140, 110, 110), special_flags=pygame.BLEND_RGB_ADD)

        # Estados que mudam a cor
        if getattr(personagem, "congelado", False):
            desenho = desenho.copy()
            desenho.fill((0, 50, 110), special_flags=pygame.BLEND_RGB_ADD)
        if esta_envenenado(personagem):
            desenho = desenho.copy()
            desenho.fill((0, 35, 0), special_flags=pygame.BLEND_RGB_ADD)
        if getattr(personagem, "esquivando", False):
            desenho = desenho.copy()
            desenho.set_alpha(110)

        # Sombra no chão (menor quando flutua)
        largura_sombra = 90 if flutua else 120
        sombra = pygame.Surface((largura_sombra, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 90), (0, 0, largura_sombra, 24))
        tela.blit(sombra, (x - largura_sombra // 2 + dx, CHAO_Y - 12))

        if not personagem.esta_vivo():
            # Derrotado: deitado e meio transparente
            caido = pygame.transform.rotate(desenho, 90 * direcao)
            caido.set_alpha(170)
            tela.blit(caido, (x - caido.get_width() // 2, CHAO_Y - caido.get_height() + 15))
            return

        topo = CHAO_Y - desenho.get_height() * 0.95 + dy
        tela.blit(desenho, (x - desenho.get_width() // 2 + dx, topo))

        cx = x + dx
        cy = CHAO_Y - 120 + dy

        # Escudo de Luz: bolha dourada
        if getattr(personagem, "escudo_de_luz", False):
            raio = 105 + self.balanco(0, 4)
            efeitos.desenhar_brilho(tela, (255, 225, 120), (cx, cy), raio, 45)
            pygame.draw.circle(tela, (255, 230, 150), (int(cx), int(cy)), int(raio), 2)

        # Veneno: bolhas verdes subindo
        if esta_envenenado(personagem):
            for i in range(4):
                fase = (self.tempo * 0.8 + i * 0.25) % 1
                bx = cx + math.sin(i * 2.3 + self.tempo * 2) * 40
                by = cy + 60 - fase * 130
                pygame.draw.circle(tela, VERDE_VENENO, (int(bx), int(by)), int(5 * (1 - fase)) + 1, 2)

        # Paralisado: teia por cima
        if esta_paralisado(personagem):
            for i in range(8):
                angulo = i * math.pi / 4
                fim = (cx + math.cos(angulo) * 70, cy + math.sin(angulo) * 90)
                pygame.draw.line(tela, (235, 235, 245), (cx, cy), fim, 2)
            for raio in (30, 55):
                pygame.draw.ellipse(tela, (235, 235, 245), (cx - raio, cy - raio * 1.3, raio * 2, raio * 2.6), 2)

    def estados_do(self, personagem):
        """Lista de etiquetas (texto, cor) mostradas no painel."""
        estados = []
        if esta_envenenado(personagem):
            estados.append((f"VENENO {personagem.veneno_turnos}", VERDE_VENENO))
        if esta_paralisado(personagem):
            estados.append(("PARALISADO", (220, 220, 255)))
        if getattr(personagem, "congelado", False):
            estados.append(("CONGELADO", (150, 220, 255)))
        if getattr(personagem, "escudo_de_luz", False):
            estados.append(("ESCUDO", DOURADO))
        if getattr(personagem, "esquivando", False):
            estados.append(("ESQUIVA", ROXO_ENERGIA))
        if isinstance(personagem, Golem) and personagem.carregado:
            estados.append(("CARREGADO", (255, 170, 70)))
        if isinstance(personagem, Esqueleto) and not personagem.ja_renasceu:
            estados.append(("RENASCE 1x", (150, 230, 200)))
        if isinstance(personagem, ChefeFinalDificil):
            estados.append((f"POÇÕES {len(personagem.inventario)}", (120, 230, 140)))
        return estados

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

        # Linha de baixo: recurso (mana, flechas, energia, fé) ou ataque/defesa
        recurso = recurso_do(personagem)
        if recurso is not None:
            nome, atual, maximo, cor = recurso
            self.desenhar_barra(x + 14, 82, 190, 12, atual, maximo, cor)
            self.escrever(f"{nome} {atual}", x + 316, 80, cor, self.font_pequena, direita=True)
        else:
            detalhes = f"Ataque {personagem.ataque}  |  Defesa {personagem.defesa}"
            self.escrever(detalhes, x + 14, 82, CINZA, self.font_pequena, sombra=False)

        # Etiquetas de estado embaixo do painel
        etiqueta_x = x + 6
        for texto, cor in self.estados_do(personagem):
            imagem = self.font_mini.render(texto, True, (20, 15, 30))
            largura = imagem.get_width() + 14
            pygame.draw.rect(self.screen, cor, (etiqueta_x, 117, largura, 18), border_radius=9)
            self.screen.blit(imagem, (etiqueta_x + 7, 120))
            etiqueta_x += largura + 6

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
            elif isinstance(jogador, Paladino):
                detalhe = "golpe de martelo"
            elif isinstance(jogador, Assassina):
                detalhe = "adagas: 25% de crítico, +15 energia"
            else:
                detalhe = "golpe de espada"

            opcoes = [
                ("1", "Atacar", detalhe, True),
                ("2", "Usar item", f"{len(jogador.inventario)} itens", len(jogador.inventario) > 0),
                ("3", "Fugir", "abandona a batalha", True),
            ]
            if habilidades_do(jogador) is not None:
                opcoes.append(("4", jogador.nome_habilidade, "abrir lista", jogador.pode_usar_habilidade()))
            return "AÇÕES", opcoes

        if self.tela == "armas":
            opcoes = []
            for i, arma in enumerate(jogador.armas, start=1):
                opcoes.append((str(i), arma.nome, arma.descricao, True))
            opcoes.append(("0", "Voltar", "", True))
            return "ESCOLHA A ARMA", opcoes

        if self.tela == "habilidades":
            titulo, lista, pode_usar, usar, tipo = habilidades_do(jogador)
            opcoes = []
            for i, habilidade in enumerate(lista, start=1):
                detalhe = f"{texto_do_custo(jogador, habilidade)} - {habilidade.descricao}"
                opcoes.append((str(i), habilidade.nome, detalhe, pode_usar(habilidade)))
            opcoes.append(("0", "Voltar", "", True))
            return titulo, opcoes

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
        esperando = self.ocupado() and self.tela != "fim"

        # Borda dourada quando é a vez do jogador
        if esperando or self.tela == "fim":
            cor_borda = BORDA_PAINEL
        else:
            pulso = 0.5 + 0.5 * math.sin(self.tempo * 4)
            cor_borda = (255, int(170 + 50 * pulso), 80)
        self.desenhar_painel(x, y, largura, altura, cor_borda)

        titulo, opcoes = self.opcoes_do_menu()
        if esperando:
            if self.pendente[1] in (self.turno_do_inimigo, self.inicio_turno_jogador):
                titulo = "TURNO DO INIMIGO..."
            else:
                titulo = "AGUARDE..."
        self.escrever(titulo, x + 16, y + 10, DOURADO, self.font)

        linha_y = y + 40
        for tecla, nome, detalhe, disponivel in opcoes:
            ativo = disponivel and not esperando
            cor_caixa = (55, 45, 90) if ativo else (35, 30, 50)
            cor_texto = BRANCO if ativo else CINZA_ESCURO

            pygame.draw.rect(self.screen, cor_caixa, (x + 12, linha_y, largura - 24, 31), border_radius=8)

            pygame.draw.rect(self.screen, DOURADO if ativo else CINZA_ESCURO,
                             (x + 16, linha_y + 4, 24, 23), border_radius=6)
            self.escrever(tecla, x + 28, linha_y + 7, (25, 20, 35), self.font_pequena, centro=True, sombra=False)

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
        if "VENEN" in texto or "veneno" in texto or "envenenou" in texto:
            return VERDE_VENENO
        if "PARALIS" in texto or "paralisado" in texto:
            return (220, 220, 255)
        if "recuperou" in texto or "sugando" in texto:
            return VERDE
        if "congel" in texto:
            return (150, 220, 255)
        if "MALDIÇÃO" in texto or "esquivou" in texto or "sombras" in texto:
            return ROXO_ENERGIA
        if "Escudo" in texto or "Sagrad" in texto:
            return DOURADO
        if "ESMAGOU" in texto or "carregando" in texto:
            return (255, 170, 70)
        if "levantou" in texto:
            return (150, 230, 200)
        if " VS " in texto:
            return DOURADO
        return BRANCO

    def desenhar_mensagens(self):
        x, y, largura, altura = 392, 414, 552, 212
        self.desenhar_painel(x, y, largura, altura)
        self.escrever("REGISTRO DA BATALHA", x + 16, y + 10, DOURADO, self.font)

        # Quebra as mensagens em linhas (guardando a cor de cada uma).
        # As mensagens mais antigas ficam mais apagadas.
        linhas = []
        for i, mensagem in enumerate(self.mensagens):
            cor = self.cor_da_mensagem(mensagem)
            if i < len(self.mensagens) - 3:
                cor = tuple(int(c * 0.65) for c in cor)
            for linha in self.quebrar_texto(mensagem, largura - 32, self.font_pequena):
                linhas.append((linha, cor))

        linha_y = y + 42
        for linha, cor in linhas[-8:]:
            self.escrever(linha, x + 16, linha_y, cor, self.font_pequena, sombra=False)
            linha_y += 20

    def desenhar_tela_batalha(self):
        arena = self.arena
        arena.blit(self.fundo_batalha, (0, 0))
        self.desenhar_ambiente(arena)

        # Quem está atacando é desenhado por cima
        if self.deslocamento(self.inimigo) != 0 and self.tela != "fim":
            ordem = [(self.jogador, X_JOGADOR, 1), (self.inimigo, X_INIMIGO, -1)]
        else:
            ordem = [(self.inimigo, X_INIMIGO, -1), (self.jogador, X_JOGADOR, 1)]
        for personagem, x, direcao in ordem:
            self.desenhar_lutador(arena, personagem, x, direcao)

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
            y = 200 - imagem.get_height() // 2
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

    def desenhar_transicao(self):
        # Escurecimento que some aos poucos depois de trocar de tela
        passado = self.tempo - self.inicio_transicao
        if passado < 0.35:
            escuro = pygame.Surface((WIDTH, HEIGHT))
            escuro.fill((5, 3, 12))
            escuro.set_alpha(int(255 * (1 - passado / 0.35)))
            self.screen.blit(escuro, (0, 0))

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

        self.desenhar_transicao()
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


# ============================================================
# INÍCIO DO PROGRAMA
# ============================================================

if __name__ == "__main__":

    game = Game()

    game.run()
