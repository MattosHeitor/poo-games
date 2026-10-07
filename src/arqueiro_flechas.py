from arqueiro import Arqueiro
from flechas import FlechaComum, FlechaDeFogo, FlechaPerfurante, FlechaDupla


class ArqueiroFlechas(Arqueiro):
    """Arqueiro que escolhe, a cada turno, qual tipo de flecha vai disparar.

    Herda do Arqueiro tudo o que já existe (flechas, adaga, aljava).
    A habilidade especial passa a ser a escolha do tipo de flecha.
    """

    nome_habilidade = "Escolher flecha"

    def __init__(self, nome):
        super().__init__(nome)
        self.tipos_flecha = [FlechaComum(), FlechaDeFogo(), FlechaPerfurante(), FlechaDupla()]

    def pode_disparar(self, flecha):
        return self.flechas >= flecha.custo

    def pode_usar_habilidade(self):
        # Pode usar se tiver flechas para pelo menos um tipo
        for flecha in self.tipos_flecha:
            if self.pode_disparar(flecha):
                return True
        return False

    def usar_habilidade(self, alvo):
        # Sem escolha, dispara a flecha de fogo (igual ao antigo tiro certeiro)
        return self.disparar(self.tipos_flecha[1], alvo)

    def disparar(self, flecha, alvo):
        if not self.pode_disparar(flecha):
            print(self.mensagem_sem_recurso)
            return 0

        self.flechas -= flecha.custo
        dano = flecha.disparar(self, alvo)
        print(f"(Flechas restantes: {self.flechas})")
        return dano
