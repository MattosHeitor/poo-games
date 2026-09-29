from personagem import Personagem


class Guerreiro(Personagem):

    def __init__(self, nome):
        super().__init__(
            nome=nome,
            vida=120,
            ataque=20,
            defesa=15
        )

    def atacar(self, alvo):
        """Golpe físico: causa dano igual ao ataque, reduzido pela defesa do alvo."""
        dano = alvo.receber_dano(self.ataque)
        print(f"{self.nome} atacou {alvo.nome} e causou {dano} de dano!")
        return dano
