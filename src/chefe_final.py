from inimigo import Inimigo


class ChefeFinal(Inimigo):
    """Chefe final: mais forte que os inimigos comuns e com golpe especial.

    A cada INTERVALO_GOLPE ataques, em vez do ataque normal, executa o
    "Golpe Devastador": 1,5x o ataque (ainda reduzido pela defesa do alvo).
    """

    INTERVALO_GOLPE = 3

    def __init__(self, nome="Lorde Sombrio"):
        super().__init__(
            nome=nome,
            vida=160,
            ataque=22,
            defesa=8
        )

        self.ataques_realizados = 0

    def atacar(self, alvo):
        """Ataque normal, ou Golpe Devastador a cada INTERVALO_GOLPE ataques."""
        self.ataques_realizados += 1

        if self.ataques_realizados % self.INTERVALO_GOLPE == 0:
            dano = alvo.receber_dano(int(self.ataque * 1.5))
            print(f"!!! {self.nome} desfere o GOLPE DEVASTADOR em {alvo.nome} e causa {dano} de dano!")
        else:
            dano = alvo.receber_dano(self.ataque)
            print(f"{self.nome} atacou {alvo.nome} e causou {dano} de dano!")
        return dano
