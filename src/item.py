class Item:
    """Item de cura: restaura `valor` pontos de vida (poção de cura)."""

    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor

    def usar(self, personagem):
        """Aplica o efeito no personagem.

        Devolve True se o item foi realmente usado (e deve ser consumido)
        ou False se não teve efeito (o item é mantido e o turno não é gasto).
        """
        if personagem.vida >= personagem.vida_maxima:
            print("A vida já está cheia. O item não foi usado.")
            return False

        curado = personagem.curar(self.valor)
        print(f"{personagem.nome} usou {self.nome} e recuperou {curado} de vida!")
        return True


class PocaoMana(Item):
    """Item que restaura `valor` pontos de mana (só faz efeito em quem tem mana)."""

    def usar(self, personagem):
        if not hasattr(personagem, "recuperar_mana"):
            print(f"{personagem.nome} não usa mana. O item não foi usado.")
            return False

        if personagem.mana >= personagem.MANA_MAXIMA:
            print("A mana já está cheia. O item não foi usado.")
            return False

        recuperada = personagem.recuperar_mana(self.valor)
        print(f"{personagem.nome} usou {self.nome} e recuperou {recuperada} de mana!")
        return True
