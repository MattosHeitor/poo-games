class Item:
    """Classe base dos itens consumíveis do inventário.

    Cada item tem um `nome` e um `valor` (a intensidade do efeito). As
    subclasses implementam `usar`, que aplica o efeito num personagem.
    """

    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor

    def usar(self, personagem):
        """Aplica o efeito no personagem.

        Devolve True se o item foi realmente usado (e deve ser consumido)
        ou False se não teve efeito (o item é mantido e o turno não é gasto).
        """
        raise NotImplementedError("Subclasses de Item devem implementar usar().")


class PocaoVida(Item):
    """Poção de Vida: restaura `valor` pontos de vida (sem passar do máximo)."""

    def __init__(self, nome="Poção de Vida", valor=40):
        super().__init__(nome, valor)

    def usar(self, personagem):
        if personagem.vida >= personagem.vida_maxima:
            print("A vida já está cheia. O item não foi usado.")
            return False

        curado = personagem.curar(self.valor)
        print(f"{personagem.nome} usou {self.nome} e recuperou {curado} de vida!")
        return True


class PocaoMana(Item):
    """Poção de Mana: restaura `valor` de mana (só faz efeito em quem tem mana)."""

    def __init__(self, nome="Poção de Mana", valor=30):
        super().__init__(nome, valor)

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


class Aljava(Item):
    """Aljava: repõe `valor` flechas (só faz efeito em quem usa flechas)."""

    def __init__(self, nome="Aljava", valor=6):
        super().__init__(nome, valor)

    def usar(self, personagem):
        if not hasattr(personagem, "recuperar_flechas"):
            print(f"{personagem.nome} não usa flechas. O item não foi usado.")
            return False

        if personagem.flechas >= personagem.FLECHAS_MAXIMAS:
            print("A aljava já está cheia. O item não foi usado.")
            return False

        recuperadas = personagem.recuperar_flechas(self.valor)
        print(f"{personagem.nome} usou {self.nome} e recuperou {recuperadas} flechas!")
        return True
