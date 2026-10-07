import random

from personagem import Personagem
from tecnicas import LaminaEnvenenada, GolpeNasSombras, Esquiva


class Assassina(Personagem):
    """Personagem rápida e frágil que usa energia para suas técnicas.

    - Ataque normal: adagas, com 25% de chance de crítico (2x),
      e recupera 15 de energia.
    """

    nome_habilidade = "Técnicas"
    mensagem_sem_recurso = "A assassina não possui energia suficiente."

    ENERGIA_MAXIMA = 100
    RECUPERACAO_ENERGIA = 15
    CHANCE_CRITICO = 0.25

    def __init__(self, nome):
        super().__init__(
            nome=nome,
            vida=85,
            ataque=26,
            defesa=6
        )

        self.energia = self.ENERGIA_MAXIMA
        self.esquivando = False
        self.ultimo_critico = False   # a interface usa para mostrar o efeito
        self.tecnicas = [LaminaEnvenenada(), GolpeNasSombras(), Esquiva()]

    def atacar(self, alvo):
        self.ultimo_critico = random.random() < self.CHANCE_CRITICO

        if self.ultimo_critico:
            dano = alvo.receber_dano(self.ataque * 2)
            print(f"ACERTO CRÍTICO! {self.nome} cravou as adagas em {alvo.nome} e causou {dano} de dano!")
        else:
            dano = alvo.receber_dano(self.ataque)
            print(f"{self.nome} golpeou {alvo.nome} com as adagas e causou {dano} de dano!")

        self.recuperar_energia(self.RECUPERACAO_ENERGIA)
        return dano

    def recuperar_energia(self, quantidade):
        energia_anterior = self.energia
        self.energia = min(self.ENERGIA_MAXIMA, self.energia + quantidade)
        return self.energia - energia_anterior

    def pode_usar_tecnica(self, tecnica):
        return self.energia >= tecnica.custo

    def pode_usar_habilidade(self):
        for tecnica in self.tecnicas:
            if self.pode_usar_tecnica(tecnica):
                return True
        return False

    def usar_habilidade(self, alvo):
        # Sem escolha, usa o Golpe nas Sombras
        return self.usar_tecnica(self.tecnicas[1], alvo)

    def usar_tecnica(self, tecnica, alvo):
        if not self.pode_usar_tecnica(tecnica):
            print(self.mensagem_sem_recurso)
            return 0

        self.energia -= tecnica.custo
        dano = tecnica.usar(self, alvo)
        print(f"(Energia restante: {self.energia})")
        return dano

    def receber_dano(self, dano, ignorar_defesa=False):
        # Com a Esquiva ativa, o próximo ataque não acerta
        if self.esquivando:
            self.esquivando = False
            print(f"{self.nome} se esquivou do ataque!")
            return 0

        return super().receber_dano(dano, ignorar_defesa)

    def _extras_status(self):
        return f" | Energia: {self.energia}/{self.ENERGIA_MAXIMA}"
