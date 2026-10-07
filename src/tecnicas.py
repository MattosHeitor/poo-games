from estados import envenenar


class Tecnica:
    """Classe base das técnicas da assassina. Cada técnica gasta energia."""

    def __init__(self, nome, custo, descricao):
        self.nome = nome
        self.custo = custo
        self.descricao = descricao

    def usar(self, assassina, alvo):
        raise NotImplementedError("Subclasses de Tecnica devem implementar usar().")


class LaminaEnvenenada(Tecnica):

    DANO_INICIAL = 10
    DANO_POR_TURNO = 8
    TURNOS = 3

    def __init__(self):
        super().__init__("Veneno", 30, "10 agora + 8 por turno (3 turnos)")

    def usar(self, assassina, alvo):
        dano = alvo.receber_dano(self.DANO_INICIAL, ignorar_defesa=True)
        envenenar(alvo, self.DANO_POR_TURNO, self.TURNOS)
        print(f"{assassina.nome} envenenou {alvo.nome} e causou {dano} de dano!")
        return dano


class GolpeNasSombras(Tecnica):

    def __init__(self):
        super().__init__("Golpe nas Sombras", 40, "2x o ataque")

    def usar(self, assassina, alvo):
        dano = alvo.receber_dano(assassina.ataque * 2)
        print(f"{assassina.nome} surgiu das sombras e golpeou {alvo.nome}, causando {dano} de dano!")
        return dano


class Esquiva(Tecnica):

    def __init__(self):
        super().__init__("Esquiva", 20, "desvia do próximo ataque")

    def usar(self, assassina, alvo):
        assassina.esquivando = True
        print(f"{assassina.nome} se escondeu nas sombras!")
        return 0
