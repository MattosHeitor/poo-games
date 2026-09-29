from src.guerreiro import Guerreiro
from src.mago import Mago
from src.item import Item, PocaoMana


def test_pocao_de_cura_recupera_vida():
    guerreiro = Guerreiro("Arthur")
    guerreiro.vida = 50

    usado = Item("Poção de Cura", 40).usar(guerreiro)

    assert usado is True
    assert guerreiro.vida == 90


def test_pocao_de_cura_nao_ultrapassa_maximo():
    guerreiro = Guerreiro("Arthur")
    guerreiro.vida = 110

    Item("Poção de Cura", 40).usar(guerreiro)

    assert guerreiro.vida == 120


def test_pocao_de_cura_com_vida_cheia_nao_e_usada():
    guerreiro = Guerreiro("Arthur")

    assert Item("Poção de Cura", 40).usar(guerreiro) is False


def test_pocao_de_mana_recupera_mana():
    mago = Mago("Merlin")
    mago.mana = 40

    usado = PocaoMana("Poção de Mana", 30).usar(mago)

    assert usado is True
    assert mago.mana == 70


def test_pocao_de_mana_sem_efeito_no_guerreiro():
    guerreiro = Guerreiro("Arthur")

    assert PocaoMana("Poção de Mana", 30).usar(guerreiro) is False
