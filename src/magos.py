from mago import Mago
from magias import BolaDeFogo, Explosao, LancaDeGelo, Congelar, Faisca, Tempestade


class MagoElemental(Mago):
    """Mago que escolhe, a cada turno, qual das suas magias vai lançar.

    Herda do Mago tudo o que já existe (vida, mana, ataque com o cajado).
    Cada tipo de mago (subclasse) define o seu elemento e a sua lista de magias.
    """

    elemento = ""
    nome_habilidade = "Magias"

    def __init__(self, nome):
        super().__init__(nome)
        self.magias = []

    def pode_lancar(self, magia):
        return self.mana >= magia.custo

    def pode_usar_habilidade(self):
        # Pode usar a habilidade se tiver mana para pelo menos uma magia
        for magia in self.magias:
            if self.pode_lancar(magia):
                return True
        return False

    def usar_habilidade(self, alvo):
        # Sem escolha, lança a primeira magia da lista
        return self.lancar_magia(self.magias[0], alvo)

    def lancar_magia(self, magia, alvo):
        if not self.pode_lancar(magia):
            print(self.mensagem_sem_recurso)
            return 0

        self.mana -= magia.custo
        dano = magia.lancar(self, alvo)
        print(f"(Mana restante: {self.mana})")
        return dano


class MagoFogo(MagoElemental):

    elemento = "Fogo"

    def __init__(self, nome):
        super().__init__(nome)
        self.magias = [BolaDeFogo(), Explosao()]


class MagoGelo(MagoElemental):

    elemento = "Gelo"

    def __init__(self, nome):
        super().__init__(nome)
        self.magias = [LancaDeGelo(), Congelar()]


class MagoRaio(MagoElemental):

    elemento = "Raio"

    def __init__(self, nome):
        super().__init__(nome)
        self.magias = [Faisca(), Tempestade()]
