from abc import ABC, abstractmethod


class Personagem(ABC):
    """Classe base abstrata de todo personagem (jogador ou inimigo).

    Guarda os atributos comuns (vida, ataque, defesa, inventário) e implementa
    o que é igual para todos: receber dano, curar e mostrar status. Cada
    subclasse define como ataca (`atacar`) e, opcionalmente, uma habilidade
    especial (`nome_habilidade`, `pode_usar_habilidade`, `usar_habilidade`).
    """

    # Habilidade especial (opcional). None = o personagem não possui.
    nome_habilidade = None
    mensagem_sem_recurso = "Recursos insuficientes para usar a habilidade."

    def __init__(self, nome, vida, ataque, defesa):
        self.nome = nome
        self.vida = vida
        self.vida_maxima = vida   # limite para a cura
        self.ataque = ataque
        self.defesa = defesa
        self.inventario = []      # lista de objetos Item

    def esta_vivo(self):
        return self.vida > 0

    def receber_dano(self, dano, ignorar_defesa=False):
        """Aplica dano ao personagem e devolve o dano efetivamente sofrido.

        - O dano é reduzido pela defesa (dano - defesa).
        - O dano mínimo é 1, para que nenhum ataque seja totalmente anulado
          (evita batalhas impossíveis de vencer quando defesa >= ataque).
        - Com ignorar_defesa=True (usado pela magia), a defesa não é considerada.
        - A vida nunca fica negativa.
        """
        if ignorar_defesa:
            dano_real = dano
        else:
            dano_real = max(1, dano - self.defesa)

        self.vida = max(0, self.vida - dano_real)
        return dano_real

    def curar(self, quantidade):
        """Recupera vida (sem ultrapassar a vida máxima) e devolve o valor curado."""
        vida_anterior = self.vida
        self.vida = min(self.vida_maxima, self.vida + quantidade)
        return self.vida - vida_anterior

    def adicionar_item(self, item):
        """Guarda um item no inventário do personagem."""
        self.inventario.append(item)

    @abstractmethod
    def atacar(self, alvo):
        """Ataque básico contra `alvo`; cada subclasse define o seu."""

    def pode_usar_habilidade(self):
        """Indica se a habilidade especial está disponível (padrão: não)."""
        return False

    def usar_habilidade(self, alvo):
        """Executa a habilidade especial. Sobrescrita por quem tem uma."""
        raise NotImplementedError(f"{self.nome} não possui habilidade especial.")

    def _barra_vida(self, tamanho=20):
        """Barra de vida em ASCII, ex.: [##########----------]."""
        cheios = round(tamanho * self.vida / self.vida_maxima)
        return "[" + "#" * cheios + "-" * (tamanho - cheios) + "]"

    def _extras_status(self):
        """Texto extra do status; subclasses (ex.: Mago) podem sobrescrever."""
        return ""

    def mostrar_status(self):
        print(
            f"{self.nome:<14} "
            f"Vida {self._barra_vida()} {self.vida}/{self.vida_maxima} | "
            f"Ataque: {self.ataque} | "
            f"Defesa: {self.defesa}"
            f"{self._extras_status()}"
        )
