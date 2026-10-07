from guerreiro import Guerreiro
from mago import Mago
from arqueiro import Arqueiro
from inimigo import Inimigo
from vampiro import Vampiro
from chefe_final import ChefeFinal
from item import PocaoVida, PocaoMana, Aljava
from batalha import Batalha

# Catálogo de inimigos: opção -> (dificuldade, fábrica que cria um inimigo novo).
# Usar fábricas garante um inimigo "zerado" a cada batalha.
INIMIGOS = {
    "1": ("fácil", lambda: Inimigo("Goblin", vida=100, ataque=15, defesa=5)),
    "2": ("médio", lambda: Inimigo("Orc", vida=150, ataque=25, defesa=10)),
    "3": ("difícil", lambda: Inimigo("Dragão Jovem", vida=140, ataque=28, defesa=8)),
    "4": ("difícil - suga vida", lambda: Vampiro()),
    "5": ("CHEFE FINAL", lambda: ChefeFinal()),
}


def ler_opcao(mensagem, validas):
    """Repete a pergunta até o jogador digitar uma das opções válidas."""
    while True:
        opcao = input(mensagem).strip()
        if opcao in validas:
            return opcao
        print("Opção inválida.")


def escolher_jogador():
    """Pergunta a classe e o nome, e devolve o personagem com itens iniciais."""
    print("\nEscolha sua classe:")
    print("1 - Guerreiro (Vida 120 | Ataque 20 | Defesa 15)")
    print("2 - Mago      (Vida 80  | Ataque 30 | Defesa 5  | usa magia e mana)")
    print("3 - Arqueiro  (Vida 100 | Ataque 22 | Defesa 8  | usa flechas)")
    classe = ler_opcao("Classe: ", ("1", "2", "3"))

    nome = input("Nome do herói: ").strip()

    if classe == "1":
        jogador = Guerreiro(nome or "Arthur")
    elif classe == "2":
        jogador = Mago(nome or "Merlin")
        jogador.adicionar_item(PocaoMana())
    else:
        jogador = Arqueiro(nome or "Robin")
        jogador.adicionar_item(Aljava())

    # Itens iniciais de todas as classes
    jogador.adicionar_item(PocaoVida())
    jogador.adicionar_item(PocaoVida())
    return jogador


def escolher_inimigo():
    """Mostra o catálogo de inimigos e devolve o escolhido."""
    print("\nEscolha seu adversário:")
    for chave, (dificuldade, fabrica) in INIMIGOS.items():
        inimigo = fabrica()
        print(
            f"{chave} - {inimigo.nome} ({dificuldade}) | "
            f"Vida {inimigo.vida} | Ataque {inimigo.ataque} | Defesa {inimigo.defesa}"
        )
    chave = ler_opcao("Inimigo: ", tuple(INIMIGOS))

    return INIMIGOS[chave][1]()


def main():
    print("=" * 60)
    print("                   JOGO DE BATALHA")
    print("=" * 60)

    while True:
        jogador = escolher_jogador()
        inimigo = escolher_inimigo()

        Batalha(jogador, inimigo).iniciar()

        if ler_opcao("\nJogar novamente? (s/n): ", ("s", "n")) == "n":
            print("Até a próxima!")
            break


if __name__ == "__main__":
    main()
