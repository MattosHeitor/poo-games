from personagem import Personagem


class Inimigo(Personagem):

    def __init__(self, nome, vida, ataque, defesa):
        super().__init__(
            nome=nome,
            vida=vida,
            ataque=ataque,
            defesa=defesa
        )

    def atacar(self, alvo):
        """Ataque básico: causa dano igual ao ataque, reduzido pela defesa do alvo."""
        dano = alvo.receber_dano(self.ataque)
        print(f"{self.nome} atacou {alvo.nome} e causou {dano} de dano!")
        return dano
