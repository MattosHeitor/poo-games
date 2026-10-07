from src.main import escolher_jogador, escolher_inimigo, ler_opcao
# src/main.py importa "guerreiro" e "mago" como módulos de topo; usamos o mesmo
# caminho aqui para que isinstance() compare a mesma classe.
from guerreiro import Guerreiro
from mago import Mago
from arqueiro import Arqueiro
from vampiro import Vampiro
from chefe_final import ChefeFinal


def simular_entradas(monkeypatch, entradas):
    iterador = iter(entradas)
    monkeypatch.setattr("builtins.input", lambda _="": next(iterador))


def test_ler_opcao_repete_ate_ser_valida(monkeypatch):
    simular_entradas(monkeypatch, ["x", "", "2"])

    assert ler_opcao("? ", ("1", "2")) == "2"


def test_escolher_guerreiro_com_itens_iniciais(monkeypatch):
    simular_entradas(monkeypatch, ["1", "Arthur"])

    jogador = escolher_jogador()

    assert isinstance(jogador, Guerreiro)
    assert jogador.nome == "Arthur"
    assert len(jogador.inventario) == 2


def test_escolher_mago_recebe_pocao_de_mana(monkeypatch):
    simular_entradas(monkeypatch, ["2", ""])  # nome vazio -> nome padrão

    jogador = escolher_jogador()

    assert isinstance(jogador, Mago)
    assert jogador.nome == "Merlin"
    assert len(jogador.inventario) == 3


def test_escolher_inimigo(monkeypatch):
    simular_entradas(monkeypatch, ["2"])

    inimigo = escolher_inimigo()

    assert inimigo.nome == "Orc"
    assert inimigo.vida == 150


def test_escolher_arqueiro_recebe_aljava(monkeypatch):
    simular_entradas(monkeypatch, ["3", ""])

    jogador = escolher_jogador()

    assert isinstance(jogador, Arqueiro)
    assert jogador.nome == "Robin"
    assert len(jogador.inventario) == 3


def test_escolher_vampiro(monkeypatch):
    simular_entradas(monkeypatch, ["4"])

    assert isinstance(escolher_inimigo(), Vampiro)


def test_escolher_chefe_final(monkeypatch):
    simular_entradas(monkeypatch, ["5"])

    assert isinstance(escolher_inimigo(), ChefeFinal)


def test_cada_escolha_cria_um_inimigo_novo(monkeypatch):
    simular_entradas(monkeypatch, ["1", "1"])

    primeiro = escolher_inimigo()
    primeiro.receber_dano(50)
    segundo = escolher_inimigo()

    assert segundo.vida == 100
