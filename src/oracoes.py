class Oracao:
    """Classe base das orações do paladino. Cada oração gasta Fé."""

    def __init__(self, nome, custo, descricao):
        self.nome = nome
        self.custo = custo
        self.descricao = descricao

    def pode_usar(self, paladino):
        # Algumas orações só fazem sentido em certas situações
        return True

    def usar(self, paladino, alvo):
        raise NotImplementedError("Subclasses de Oracao devem implementar usar().")


class CuraSagrada(Oracao):

    CURA = 35

    def __init__(self):
        super().__init__("Cura Sagrada", 1, "recupera 35 de vida")

    def pode_usar(self, paladino):
        # Não gasta Fé com a vida cheia
        return paladino.vida < paladino.vida_maxima

    def usar(self, paladino, alvo):
        curado = paladino.curar(self.CURA)
        print(f"{paladino.nome} rezou a Cura Sagrada e recuperou {curado} de vida!")
        return 0


class GolpeSagrado(Oracao):

    def __init__(self):
        super().__init__("Golpe Sagrado", 1, "1,5x o ataque, ignora defesa")

    def usar(self, paladino, alvo):
        dano = alvo.receber_dano(int(paladino.ataque * 1.5), ignorar_defesa=True)
        print(f"{paladino.nome} desferiu o Golpe Sagrado em {alvo.nome} e causou {dano} de dano!")
        return dano


class EscudoDeLuz(Oracao):

    def __init__(self):
        super().__init__("Escudo de Luz", 1, "próximo ataque inimigo causa metade")

    def pode_usar(self, paladino):
        # Não adianta usar com o escudo já ativo
        return not paladino.escudo_de_luz

    def usar(self, paladino, alvo):
        paladino.escudo_de_luz = True
        print(f"{paladino.nome} ergueu um Escudo de Luz!")
        return 0
