from personagem import Personagem


class Arqueiro(Personagem):
    """Personagem de ataque à distância que depende de flechas.

    - Ataque normal: dispara 1 flecha (dano = ataque, reduzido pela defesa).
      Sem flechas, ataca com a adaga (um terço do ataque).
    - Tiro certeiro: gasta 2 flechas e causa 1,5x o ataque (reduzido pela defesa).
    """

    FLECHAS_MAXIMAS = 12
    CUSTO_TIRO = 2

    nome_habilidade = "Tiro certeiro"
    mensagem_sem_recurso = "O arqueiro não possui flechas suficientes."

    def __init__(self, nome):
        super().__init__(
            nome=nome,
            vida=100,
            ataque=22,
            defesa=8
        )

        self.flechas = self.FLECHAS_MAXIMAS

    def atacar(self, alvo):
        """Dispara uma flecha; sem flechas, usa a adaga (dano reduzido)."""
        if self.flechas > 0:
            self.flechas -= 1
            dano = alvo.receber_dano(self.ataque)
            print(f"{self.nome} disparou uma flecha em {alvo.nome} e causou {dano} de dano!")
        else:
            dano = alvo.receber_dano(self.ataque // 3)
            print(f"{self.nome} está sem flechas e golpeou {alvo.nome} com a adaga, causando {dano} de dano!")
        return dano

    def recuperar_flechas(self, quantidade):
        """Repõe flechas (sem passar do máximo) e devolve quantas foram repostas."""
        flechas_anteriores = self.flechas
        self.flechas = min(self.FLECHAS_MAXIMAS, self.flechas + quantidade)
        return self.flechas - flechas_anteriores

    def pode_usar_habilidade(self):
        return self.flechas >= self.CUSTO_TIRO

    def usar_habilidade(self, alvo):
        return self.tiro_certeiro(alvo)

    def tiro_certeiro(self, alvo):
        """Tiro potente: 1,5x o ataque, gasta CUSTO_TIRO flechas."""
        if not self.pode_usar_habilidade():
            print(self.mensagem_sem_recurso)
            return 0

        self.flechas -= self.CUSTO_TIRO
        dano = alvo.receber_dano(int(self.ataque * 1.5))
        print(
            f"{self.nome} acertou um tiro certeiro em {alvo.nome} e causou {dano} de dano! "
            f"(Flechas restantes: {self.flechas})"
        )
        return dano

    def _extras_status(self):
        return f" | Flechas: {self.flechas}/{self.FLECHAS_MAXIMAS}"
