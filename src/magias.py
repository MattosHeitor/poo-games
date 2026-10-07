class Magia:
    """Classe base das magias do mago.

    Cada magia tem um nome, um custo de mana e um elemento (usado na
    interface para escolher o efeito visual). As subclasses implementam
    `lancar`, que aplica o efeito no alvo e devolve o dano causado.
    """

    def __init__(self, nome, custo, elemento, descricao):
        self.nome = nome
        self.custo = custo
        self.elemento = elemento
        self.descricao = descricao

    def lancar(self, mago, alvo):
        raise NotImplementedError("Subclasses de Magia devem implementar lancar().")


# ============================================================
# FOGO
# ============================================================

class BolaDeFogo(Magia):

    def __init__(self):
        super().__init__("Bola de Fogo", 20, "fogo", "1,5x o ataque, ignora defesa")

    def lancar(self, mago, alvo):
        dano = alvo.receber_dano(int(mago.ataque * 1.5), ignorar_defesa=True)
        print(f"{mago.nome} lançou uma Bola de Fogo em {alvo.nome} e causou {dano} de dano!")
        return dano


class Explosao(Magia):

    def __init__(self):
        super().__init__("Explosão", 40, "fogo", "2x o ataque, ignora defesa")

    def lancar(self, mago, alvo):
        dano = alvo.receber_dano(mago.ataque * 2, ignorar_defesa=True)
        print(f"{mago.nome} causou uma Explosão em {alvo.nome} e causou {dano} de dano!")
        return dano


# ============================================================
# GELO
# ============================================================

class LancaDeGelo(Magia):

    def __init__(self):
        super().__init__("Lança de Gelo", 15, "gelo", "1x o ataque, ignora defesa")

    def lancar(self, mago, alvo):
        dano = alvo.receber_dano(mago.ataque, ignorar_defesa=True)
        print(f"{mago.nome} arremessou uma Lança de Gelo em {alvo.nome} e causou {dano} de dano!")
        return dano


class Congelar(Magia):

    def __init__(self):
        super().__init__("Congelar", 30, "gelo", "0,5x o ataque, inimigo perde a vez")

    def lancar(self, mago, alvo):
        dano = alvo.receber_dano(mago.ataque // 2, ignorar_defesa=True)

        # A interface verifica este atributo antes do inimigo atacar
        alvo.congelado = True

        print(f"{mago.nome} congelou {alvo.nome} e causou {dano} de dano!")
        return dano


# ============================================================
# RAIO
# ============================================================

class Faisca(Magia):

    def __init__(self):
        super().__init__("Faísca", 10, "raio", "0,8x o ataque, ignora defesa")

    def lancar(self, mago, alvo):
        dano = alvo.receber_dano(int(mago.ataque * 0.8), ignorar_defesa=True)
        print(f"{mago.nome} soltou uma Faísca em {alvo.nome} e causou {dano} de dano!")
        return dano


class Tempestade(Magia):

    def __init__(self):
        super().__init__("Tempestade", 35, "raio", "3 raios de 0,6x, ignoram defesa")

    def lancar(self, mago, alvo):
        dano_total = 0

        # Três raios seguidos
        for _ in range(3):
            dano_total += alvo.receber_dano(int(mago.ataque * 0.6), ignorar_defesa=True)

        print(f"{mago.nome} invocou uma Tempestade em {alvo.nome} e causou {dano_total} de dano!")
        return dano_total
