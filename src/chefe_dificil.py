import random

from chefe_final import ChefeFinal
from item import PocaoVida


class ChefeFinalDificil(ChefeFinal):
    """Chefe final mais difícil.

    Além do Golpe Devastador do ChefeFinal:
    - Tem 20% de chance de acerto crítico (dano dobrado).
    - Com a vida abaixo de 40%, usa uma Poção de Vida no lugar do ataque
      (começa com 2 poções).
    """

    CHANCE_CRITICO = 0.2
    MULTIPLICADOR_CRITICO = 2
    LIMITE_CURA = 0.4

    def __init__(self, nome="Lorde Sombrio"):
        super().__init__(nome)

        self.adicionar_item(PocaoVida())
        self.adicionar_item(PocaoVida())

        # Guarda o que o chefe fez no último turno ("ataque", "critico",
        # "devastador" ou "cura"). A interface usa para escolher o efeito.
        self.ultima_acao = "ataque"

    def precisa_curar(self):
        return self.vida < self.vida_maxima * self.LIMITE_CURA

    def atacar(self, alvo):
        # 1. Cura no lugar do ataque, se estiver com pouca vida e tiver poção
        if self.precisa_curar() and self.inventario:
            pocao = self.inventario.pop(0)
            pocao.usar(self)
            self.ultima_acao = "cura"
            return 0

        # 2. Ataque normal ou Golpe Devastador (a cada 3 ataques)
        self.ataques_realizados += 1
        devastador = self.ataques_realizados % self.INTERVALO_GOLPE == 0

        dano = self.ataque
        if devastador:
            dano = int(dano * 1.5)

        # 3. Chance de acerto crítico
        critico = random.random() < self.CHANCE_CRITICO
        if critico:
            dano = dano * self.MULTIPLICADOR_CRITICO

        dano = alvo.receber_dano(dano)

        # 4. Mensagem
        if devastador:
            texto = f"{self.nome} desfere o GOLPE DEVASTADOR em {alvo.nome}"
            self.ultima_acao = "devastador"
        else:
            texto = f"{self.nome} atacou {alvo.nome}"
            self.ultima_acao = "ataque"

        if critico:
            texto = "ACERTO CRÍTICO! " + texto
            self.ultima_acao = "critico"

        print(f"{texto} e causou {dano} de dano!")
        return dano
