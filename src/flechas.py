class Flecha:
    """Classe base dos tipos de flecha do arqueiro.

    Cada flecha tem um nome e um custo (quantas flechas gasta).
    As subclasses implementam `disparar`, que devolve o dano causado.
    """

    def __init__(self, nome, custo, descricao):
        self.nome = nome
        self.custo = custo
        self.descricao = descricao

    def disparar(self, arqueiro, alvo):
        raise NotImplementedError("Subclasses de Flecha devem implementar disparar().")


class FlechaComum(Flecha):

    def __init__(self):
        super().__init__("Flecha comum", 1, "dano normal")

    def disparar(self, arqueiro, alvo):
        dano = alvo.receber_dano(arqueiro.ataque)
        print(f"{arqueiro.nome} disparou uma flecha em {alvo.nome} e causou {dano} de dano!")
        return dano


class FlechaDeFogo(Flecha):

    def __init__(self):
        super().__init__("Flecha de fogo", 2, "1,5x o ataque")

    def disparar(self, arqueiro, alvo):
        dano = alvo.receber_dano(int(arqueiro.ataque * 1.5))
        print(f"{arqueiro.nome} disparou uma flecha de fogo em {alvo.nome} e causou {dano} de dano!")
        return dano


class FlechaPerfurante(Flecha):

    def __init__(self):
        super().__init__("Flecha perfurante", 2, "ignora a defesa")

    def disparar(self, arqueiro, alvo):
        dano = alvo.receber_dano(arqueiro.ataque, ignorar_defesa=True)
        print(f"{arqueiro.nome} disparou uma flecha perfurante em {alvo.nome} e causou {dano} de dano!")
        return dano


class FlechaDupla(Flecha):

    def __init__(self):
        super().__init__("Flecha dupla", 3, "dois disparos normais")

    def disparar(self, arqueiro, alvo):
        dano_total = 0

        # Dois disparos seguidos
        for _ in range(2):
            dano_total += alvo.receber_dano(arqueiro.ataque)

        print(f"{arqueiro.nome} disparou duas flechas em {alvo.nome} e causou {dano_total} de dano!")
        return dano_total
