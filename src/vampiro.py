from inimigo import Inimigo


class Vampiro(Inimigo):
    """Novo tipo de inimigo: suga a vida do alvo.

    Cada ataque causa dano normal e cura o vampiro em metade do dano causado.
    """

    def __init__(self, nome="Vampiro"):
        super().__init__(
            nome=nome,
            vida=120,
            ataque=29,
            defesa=12
        )

    def atacar(self, alvo):
        """Ataca e recupera vida equivalente à metade do dano causado."""
        dano = alvo.receber_dano(self.ataque)
        curado = self.curar(dano // 2)
        print(
            f"{self.nome} mordeu {alvo.nome} e causou {dano} de dano, "
            f"sugando {curado} de vida!"
        )
        return dano
