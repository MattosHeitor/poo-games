import random

from inimigo import Inimigo
from estados import envenenar, paralisar


class Esqueleto(Inimigo):
    """Quando morre pela primeira vez, se levanta com 30 de vida."""

    VIDA_AO_RENASCER = 30

    def __init__(self, nome="Esqueleto"):
        super().__init__(nome=nome, vida=90, ataque=18, defesa=12)

        self.ja_renasceu = False
        self.renascendo = False      # a interface usa para mostrar o efeito
        self.ultima_acao = "ataque"

    def tentar_renascer(self):
        if self.vida == 0 and not self.ja_renasceu:
            self.ja_renasceu = True
            self.renascendo = True
            self.vida = self.VIDA_AO_RENASCER
            print(f"{self.nome} se levantou de novo com {self.vida} de vida!")

    def receber_dano(self, dano, ignorar_defesa=False):
        dano_real = super().receber_dano(dano, ignorar_defesa)
        self.tentar_renascer()
        return dano_real

    def atacar(self, alvo):
        dano = alvo.receber_dano(self.ataque)
        print(f"{self.nome} golpeou {alvo.nome} com a espada enferrujada e causou {dano} de dano!")
        return dano


class Bruxa(Inimigo):
    """A cada 2 ataques, lança uma Maldição que ignora a defesa."""

    INTERVALO_MALDICAO = 2

    def __init__(self, nome="Bruxa do Pântano"):
        super().__init__(nome=nome, vida=110, ataque=20, defesa=6)

        self.ataques_realizados = 0
        self.ultima_acao = "ataque"

    def atacar(self, alvo):
        self.ataques_realizados += 1

        if self.ataques_realizados % self.INTERVALO_MALDICAO == 0:
            dano = alvo.receber_dano(self.ataque, ignorar_defesa=True)
            print(f"{self.nome} lançou uma MALDIÇÃO em {alvo.nome} e causou {dano} de dano!")
            self.ultima_acao = "maldicao"
        else:
            dano = alvo.receber_dano(self.ataque)
            print(f"{self.nome} atirou uma bola de lodo em {alvo.nome} e causou {dano} de dano!")
            self.ultima_acao = "ataque"

        return dano


class AranhaGigante(Inimigo):
    """A cada 2 ataques envenena (6 por turno, 3 turnos).
    Cada ataque tem 25% de chance de paralisar o alvo por 1 turno.
    """

    INTERVALO_VENENO = 2
    DANO_VENENO = 6
    TURNOS_VENENO = 3
    CHANCE_PARALISIA = 0.25

    def __init__(self, nome="Aranha Gigante"):
        super().__init__(nome=nome, vida=160, ataque=25, defesa=12)

        self.ataques_realizados = 0

        # O que aconteceu no último ataque (a interface usa para os efeitos)
        self.envenenou = False
        self.paralisou = False

    def atacar(self, alvo):
        self.ataques_realizados += 1
        self.envenenou = False
        self.paralisou = False

        dano = alvo.receber_dano(self.ataque)
        print(f"{self.nome} mordeu {alvo.nome} e causou {dano} de dano!")

        # Se o ataque foi desviado (dano 0), não aplica os efeitos
        if dano > 0:
            if self.ataques_realizados % self.INTERVALO_VENENO == 0:
                envenenar(alvo, self.DANO_VENENO, self.TURNOS_VENENO)
                print(f"{alvo.nome} foi ENVENENADO!")
                self.envenenou = True

            if random.random() < self.CHANCE_PARALISIA:
                paralisar(alvo)
                print(f"{self.nome} prendeu {alvo.nome} na teia! {alvo.nome} está PARALISADO!")
                self.paralisou = True

        return dano


class Golem(Inimigo):
    """Alterna os turnos: em um carrega a força, no outro ataca com 2x."""

    def __init__(self, nome="Golem de Pedra"):
        super().__init__(nome=nome, vida=200, ataque=24, defesa=18)

        self.carregado = False
        self.ultima_acao = "ataque"

    def atacar(self, alvo):
        if not self.carregado:
            self.carregado = True
            print(f"{self.nome} está carregando um golpe poderoso!")
            self.ultima_acao = "carregar"
            return 0

        self.carregado = False
        dano = alvo.receber_dano(self.ataque * 2)
        print(f"{self.nome} ESMAGOU {alvo.nome} e causou {dano} de dano!")
        self.ultima_acao = "esmagar"
        return dano
