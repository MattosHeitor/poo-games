class Arma:
    """Classe base das armas do bárbaro.

    As subclasses implementam `golpear`, que aplica o golpe no alvo
    e devolve o dano causado.
    """

    def __init__(self, nome, descricao):
        self.nome = nome
        self.descricao = descricao

    def golpear(self, barbaro, alvo):
        raise NotImplementedError("Subclasses de Arma devem implementar golpear().")


class Espada(Arma):

    def __init__(self):
        super().__init__("Espada", "dano igual ao ataque")

    def golpear(self, barbaro, alvo):
        dano = alvo.receber_dano(barbaro.ataque)
        print(f"{barbaro.nome} golpeou {alvo.nome} com a Espada e causou {dano} de dano!")
        return dano


class Machado(Arma):

    PERDA_DE_VIDA = 5

    def __init__(self):
        super().__init__("Machado", "1,5x o ataque, mas perde 5 de vida")

    def golpear(self, barbaro, alvo):
        dano = alvo.receber_dano(int(barbaro.ataque * 1.5))

        # O golpe pesado também cansa o bárbaro
        barbaro.vida = max(0, barbaro.vida - self.PERDA_DE_VIDA)

        print(
            f"{barbaro.nome} golpeou {alvo.nome} com o Machado e causou {dano} de dano! "
            f"(perdeu {self.PERDA_DE_VIDA} de vida)"
        )
        return dano


class Martelo(Arma):

    def __init__(self):
        super().__init__("Martelo", "dano igual ao ataque, ignora defesa")

    def golpear(self, barbaro, alvo):
        dano = alvo.receber_dano(barbaro.ataque, ignorar_defesa=True)
        print(f"{barbaro.nome} esmagou {alvo.nome} com o Martelo e causou {dano} de dano!")
        return dano
