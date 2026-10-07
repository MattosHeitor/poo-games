from personagem import Personagem
from armas import Espada, Machado, Martelo


class Barbaro(Personagem):
    """Lutador forte que escolhe, a cada turno, qual arma vai usar."""

    def __init__(self, nome):
        super().__init__(
            nome=nome,
            vida=140,
            ataque=24,
            defesa=10
        )

        self.armas = [Espada(), Machado(), Martelo()]

    def atacar(self, alvo):
        # Sem escolha, ataca com a primeira arma (Espada)
        return self.usar_arma(self.armas[0], alvo)

    def usar_arma(self, arma, alvo):
        return arma.golpear(self, alvo)
