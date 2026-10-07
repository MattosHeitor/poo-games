import contextlib
import io

import pygame

from guerreiro import Guerreiro
from mago import Mago
from arqueiro import Arqueiro
from item import PocaoVida, PocaoMana, Aljava
from main import INIMIGOS

# ============================================================
# CONFIGURAÇÕES
# ============================================================

WIDTH = 800
HEIGHT = 600

FPS = 60

COR_FUNDO = (30, 30, 30)
COR_TEXTO = (255, 255, 255)
COR_DESTAQUE = (255, 255, 0)
COR_JOGADOR = (0, 200, 255)
COR_INIMIGO = (220, 50, 50)
COR_VIDA = (50, 200, 50)
COR_BARRA_VAZIA = (80, 80, 80)

MAX_MENSAGENS = 5


# ============================================================
# CRIAÇÃO DO JOGADOR (mesmas regras do main.py)
# ============================================================

def criar_jogador(classe, nome):
    if classe == "1":
        jogador = Guerreiro(nome or "Arthur")
    elif classe == "2":
        jogador = Mago(nome or "Merlin")
        jogador.adicionar_item(PocaoMana())
    else:
        jogador = Arqueiro(nome or "Robin")
        jogador.adicionar_item(Aljava())

    # Itens iniciais de todas as classes
    jogador.adicionar_item(PocaoVida())
    jogador.adicionar_item(PocaoVida())
    return jogador


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

        self.font = pygame.font.Font(None, 30)
        self.font_pequena = pygame.font.Font(None, 24)
        self.font_titulo = pygame.font.Font(None, 56)

        self.reiniciar()

    def reiniciar(self):
        # Telas possíveis: "classe", "nome", "inimigo",
        # "batalha", "inventario" e "fim"
        self.tela = "classe"
        self.classe = None
        self.nome = ""
        self.jogador = None
        self.inimigo = None
        self.mensagens = []
        self.resultado = None

    # --------------------------------------------------------
    # MENSAGENS
    # --------------------------------------------------------

    def adicionar_mensagem(self, texto):
        self.mensagens.append(texto)
        # Guarda só as últimas mensagens
        self.mensagens = self.mensagens[-MAX_MENSAGENS:]

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

                elif self.tela == "nome":
                    self.digitar_nome(event)

                elif self.tela == "inimigo":
                    self.escolher_inimigo(event)

                elif self.tela == "batalha":
                    self.escolher_acao(event)

                elif self.tela == "inventario":
                    self.escolher_item(event)

                elif self.tela == "fim":
                    self.jogar_novamente(event)

    def escolher_classe(self, event):
        if event.unicode in ("1", "2", "3"):
            self.classe = event.unicode
            self.tela = "nome"

    def digitar_nome(self, event):
        if event.key == pygame.K_RETURN:
            self.jogador = criar_jogador(self.classe, self.nome.strip())
            self.tela = "inimigo"

        elif event.key == pygame.K_BACKSPACE:
            self.nome = self.nome[:-1]

        elif event.unicode.isprintable() and len(self.nome) < 14:
            self.nome += event.unicode

    def escolher_inimigo(self, event):
        if event.unicode in INIMIGOS:
            fabrica = INIMIGOS[event.unicode][1]
            self.inimigo = fabrica()
            self.adicionar_mensagem(
                f"{self.jogador.nome} VS {self.inimigo.nome}"
            )
            self.tela = "batalha"

    def escolher_acao(self, event):
        tecla = event.unicode

        if tecla == "1":
            self.executar(self.jogador.atacar, self.inimigo)
            self.fim_do_turno()

        elif tecla == "2":
            if self.jogador.inventario:
                self.tela = "inventario"
            else:
                self.adicionar_mensagem("Você não possui itens.")

        elif tecla == "3":
            self.adicionar_mensagem("Você fugiu da batalha!")
            self.resultado = "FUGA"
            self.tela = "fim"

        elif tecla == "4" and self.jogador.nome_habilidade is not None:
            if self.jogador.pode_usar_habilidade():
                self.executar(self.jogador.usar_habilidade, self.inimigo)
                self.fim_do_turno()
            else:
                self.adicionar_mensagem(self.jogador.mensagem_sem_recurso)

    def escolher_item(self, event):
        tecla = event.unicode
        inventario = self.jogador.inventario

        if tecla == "0":
            self.tela = "batalha"

        elif tecla.isdigit() and 1 <= int(tecla) <= len(inventario):
            item = inventario[int(tecla) - 1]
            self.tela = "batalha"

            # O item só é consumido (e o turno gasto) se teve efeito
            if self.executar(item.usar, self.jogador):
                inventario.remove(item)
                self.fim_do_turno()

    def jogar_novamente(self, event):
        if event.unicode.lower() == "s":
            self.reiniciar()
        elif event.unicode.lower() == "n":
            self.running = False

    # --------------------------------------------------------
    # TURNO
    # --------------------------------------------------------

    def fim_do_turno(self):
        # O inimigo só contra-ataca se ainda estiver vivo
        if self.inimigo.esta_vivo():
            self.executar(self.inimigo.atacar, self.jogador)

        if not self.inimigo.esta_vivo():
            self.adicionar_mensagem(f"{self.inimigo.nome} foi derrotado!")
            self.resultado = "VITÓRIA!"
            self.tela = "fim"

        elif not self.jogador.esta_vivo():
            self.adicionar_mensagem(f"{self.jogador.nome} foi derrotado!")
            self.resultado = "DERROTA..."
            self.tela = "fim"

    # --------------------------------------------------------
    # DESENHO
    # --------------------------------------------------------

    def escrever(self, texto, x, y, cor=COR_TEXTO, fonte=None):
        if fonte is None:
            fonte = self.font

        imagem = fonte.render(texto, True, cor)
        self.screen.blit(imagem, (x, y))

    def desenhar_barra_vida(self, personagem, x, y):
        largura = 200
        cheia = int(largura * personagem.vida / personagem.vida_maxima)

        pygame.draw.rect(self.screen, COR_BARRA_VAZIA, (x, y, largura, 15))
        pygame.draw.rect(self.screen, COR_VIDA, (x, y, cheia, 15))

    def desenhar_personagem(self, personagem, x, cor):
        self.escrever(personagem.nome, x, 90, COR_DESTAQUE)

        pygame.draw.rect(self.screen, cor, (x, 120, 120, 120))

        self.desenhar_barra_vida(personagem, x, 255)

        self.escrever(
            f"Vida: {personagem.vida}/{personagem.vida_maxima}",
            x, 280, fonte=self.font_pequena
        )
        self.escrever(
            f"Ataque: {personagem.ataque} | Defesa: {personagem.defesa}",
            x, 302, fonte=self.font_pequena
        )

        # Mana do Mago ou flechas do Arqueiro
        extras = personagem._extras_status().replace(" | ", "")
        if extras:
            self.escrever(extras, x, 324, fonte=self.font_pequena)

    def desenhar_mensagens(self):
        y = 480
        for mensagem in self.mensagens:
            self.escrever(mensagem, 30, y, fonte=self.font_pequena)
            y += 22

    def desenhar_tela_classe(self):
        self.escrever("JOGO DE BATALHA", 230, 60, COR_DESTAQUE, self.font_titulo)
        self.escrever("Escolha sua classe:", 80, 180)
        self.escrever("1 - Guerreiro (Vida 120 | Ataque 20 | Defesa 15)", 80, 230)
        self.escrever("2 - Mago (Vida 80 | Ataque 30 | Defesa 5 | usa magia e mana)", 80, 270)
        self.escrever("3 - Arqueiro (Vida 100 | Ataque 22 | Defesa 8 | usa flechas)", 80, 310)
        self.escrever("Pressione 1, 2 ou 3", 80, 390, COR_DESTAQUE)

    def desenhar_tela_nome(self):
        self.escrever("Nome do herói:", 80, 180)
        self.escrever(self.nome + "_", 80, 230, COR_DESTAQUE, self.font_titulo)
        self.escrever("ENTER para confirmar (vazio usa o nome padrão)", 80, 320)

    def desenhar_tela_inimigo(self):
        self.escrever("Escolha seu adversário:", 80, 120)

        y = 180
        for chave, (dificuldade, fabrica) in INIMIGOS.items():
            inimigo = fabrica()
            self.escrever(
                f"{chave} - {inimigo.nome} ({dificuldade}) | "
                f"Vida {inimigo.vida} | Ataque {inimigo.ataque} | "
                f"Defesa {inimigo.defesa}",
                80, y, fonte=self.font_pequena
            )
            y += 40

    def desenhar_tela_batalha(self):
        self.desenhar_personagem(self.jogador, 120, COR_JOGADOR)
        self.desenhar_personagem(self.inimigo, 520, COR_INIMIGO)

        if self.tela == "batalha":
            opcoes = ["1 - Atacar", "2 - Usar item", "3 - Fugir"]
            if self.jogador.nome_habilidade is not None:
                opcoes.append(f"4 - {self.jogador.nome_habilidade}")

        elif self.tela == "inventario":
            opcoes = []
            for i, item in enumerate(self.jogador.inventario, start=1):
                opcoes.append(f"{i} - {item.nome} ({item.valor})")
            opcoes.append("0 - Voltar")

        else:  # tela "fim"
            opcoes = []
            self.escrever(self.resultado, 30, 360, COR_DESTAQUE, self.font_titulo)
            self.escrever("Jogar novamente? (S/N)", 30, 410)

        y = 360
        for opcao in opcoes:
            self.escrever(opcao, 30, y)
            y += 28

        self.desenhar_mensagens()

    def draw(self):
        self.screen.fill(COR_FUNDO)

        if self.tela == "classe":
            self.desenhar_tela_classe()
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

            # 1. Eventos
            self.handle_events()

            # 2. Desenho
            self.draw()

            # Controla FPS
            self.clock.tick(FPS)

        pygame.quit()


# ============================================================
# INÍCIO DO PROGRAMA
# ============================================================

if __name__ == "__main__":

    game = Game()

    game.run()
