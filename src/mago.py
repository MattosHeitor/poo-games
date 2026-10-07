from personagem import Personagem


class Mago(Personagem):
    """Personagem frágil, mas de grande poder de ataque, que usa mana.

    - Ataque normal: golpe de cajado (metade do ataque) que recupera mana.
    - Magia: 1,5x o ataque, ignora a defesa do alvo e gasta mana.
    """

    nome_habilidade = "Usar magia"
    mensagem_sem_recurso = "O mago não possui mana suficiente."

    MANA_MAXIMA = 100
    CUSTO_MAGIA = 20          # mana gasta a cada magia
    RECUPERACAO_MANA = 10     # mana recuperada a cada ataque normal

    def __init__(self, nome):
        super().__init__(
            nome=nome,
            vida=80,
            ataque=30,
            defesa=5
        )

        self.mana = self.MANA_MAXIMA

    def atacar(self, alvo):
        """Ataque normal (cajado): metade do ataque, reduzido pela defesa.

        Em troca, o mago recupera um pouco de mana (até o máximo).
        """
        dano = alvo.receber_dano(self.ataque // 2)
        self.recuperar_mana(self.RECUPERACAO_MANA)
        print(f"{self.nome} atacou {alvo.nome} com o cajado e causou {dano} de dano!")
        return dano

    def recuperar_mana(self, quantidade):
        """Recupera mana (sem ultrapassar o máximo) e devolve o valor recuperado."""
        mana_anterior = self.mana
        self.mana = min(self.MANA_MAXIMA, self.mana + quantidade)
        return self.mana - mana_anterior

    def pode_usar_magia(self):
        """Indica se há mana suficiente para lançar uma magia."""
        return self.mana >= self.CUSTO_MAGIA

    def _extras_status(self):
        return f" | Mana: {self.mana}/{self.MANA_MAXIMA}"

    def pode_usar_habilidade(self):
        return self.pode_usar_magia()

    def usar_habilidade(self, alvo):
        return self.usar_magia(alvo)

    def usar_magia(self, alvo):
        """Magia: dano de 1,5x o ataque que IGNORA a defesa, custa mana."""
        if not self.pode_usar_magia():
            print("O mago não possui mana suficiente.")
            return 0

        self.mana -= self.CUSTO_MAGIA
        dano = alvo.receber_dano(int(self.ataque * 1.5), ignorar_defesa=True)
        print(
            f"{self.nome} lançou uma magia em {alvo.nome} e causou {dano} de dano! "
            f"(Mana restante: {self.mana})"
        )
        return dano
