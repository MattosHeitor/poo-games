from guerreiro import Guerreiro
from mago import Mago
from inimigo import Inimigo
from item import Item, PocaoMana
from batalha import Batalha
from novo inimigo import novo_inimigo

# Catálogo de inimigos: opção -> (nome, vida, ataque, defesa, dificuldade)
INIMIGOS = {
    "1": ("Goblin", 100, 15, 5, "fácil"),
    "2": ("Orc", 150, 25, 10, "médio"),
    "3": ("Dragão Jovem", 140, 28, 8, "difícil"),
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
    print("2 - Mago      (Vida 80  | Ataque 30 | Defesa 5 | usa magia)")
    classe = ler_opcao("Classe: ", ("1", "2"))

    nome = input("Nome do herói: ").strip()

    if classe == "1":
        jogador = Guerreiro(nome or "Arthur")
    else:
        jogador = Mago(nome or "Merlin")
        jogador.adicionar_item(PocaoMana("Poção de Mana", 30))

    # Itens iniciais
    jogador.adicionar_item(Item("Poção de Cura", 40))
    jogador.adicionar_item(Item("Poção de Cura", 40))
    return jogador


def escolher_inimigo():
    """Mostra o catálogo de inimigos e devolve o escolhido."""
    print("\nEscolha seu adversário:")
    for chave, (nome, vida, ataque, defesa, dificuldade) in INIMIGOS.items():
        print(f"{chave} - {nome} ({dificuldade}) | Vida {vida} | Ataque {ataque} | Defesa {defesa}")
    chave = ler_opcao("Inimigo: ", tuple(INIMIGOS))

    nome, vida, ataque, defesa, _ = INIMIGOS[chave]
    return Inimigo(nome=nome, vida=vida, ataque=ataque, defesa=defesa)


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
