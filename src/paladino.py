from personagem import Personagem
from oracoes import CuraSagrada, GolpeSagrado, EscudoDeLuz


class Paladino(Personagem):
    """Guerreiro sagrado: ataca com o martelo e usa orações que gastam Fé.

    Começa com 3 cargas de Fé, que não se recuperam durante a batalha.
    """

    nome_habilidade = "Orações"
    mensagem_sem_recurso = "Sem Fé suficiente (ou a oração não pode ser usada agora)."

    FE_MAXIMA = 3

    def __init__(self, nome):
        super().__init__(
            nome=nome,
            vida=160,
            ataque=18,
            defesa=20
        )

        self.fe = self.FE_MAXIMA
        self.escudo_de_luz = False
        self.oracoes = [CuraSagrada(), GolpeSagrado(), EscudoDeLuz()]

    def atacar(self, alvo):
        dano = alvo.receber_dano(self.ataque)
        print(f"{self.nome} golpeou {alvo.nome} com o martelo e causou {dano} de dano!")
        return dano

    def pode_orar(self, oracao):
        return self.fe >= oracao.custo and oracao.pode_usar(self)

    def pode_usar_habilidade(self):
        for oracao in self.oracoes:
            if self.pode_orar(oracao):
                return True
        return False

    def usar_habilidade(self, alvo):
        # Sem escolha, usa o Golpe Sagrado
        return self.orar(self.oracoes[1], alvo)

    def orar(self, oracao, alvo):
        if not self.pode_orar(oracao):
            print(self.mensagem_sem_recurso)
            return 0

        self.fe -= oracao.custo
        dano = oracao.usar(self, alvo)
        print(f"(Fé restante: {self.fe})")
        return dano

    def receber_dano(self, dano, ignorar_defesa=False):
        dano_real = super().receber_dano(dano, ignorar_defesa)

        # O Escudo de Luz devolve metade do dano sofrido
        if self.escudo_de_luz:
            self.escudo_de_luz = False
            bloqueado = dano_real // 2
            self.vida += bloqueado
            dano_real -= bloqueado
            print(f"O Escudo de Luz de {self.nome} bloqueou {bloqueado} de dano!")

        return dano_real
