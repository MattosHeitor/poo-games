from src.guerreiro import Guerreiro
from src.mago import Mago
import pytest

from src.arqueiro import Arqueiro
from src.item import Item, PocaoVida, PocaoMana, Aljava


def test_pocao_de_vida_recupera_vida():
    guerreiro = Guerreiro("Arthur")
    guerreiro.vida = 50

    usado = PocaoVida().usar(guerreiro)

    assert usado is True
    assert guerreiro.vida == 90


def test_pocao_de_vida_nao_ultrapassa_maximo():
    guerreiro = Guerreiro("Arthur")
    guerreiro.vida = 110

    PocaoVida().usar(guerreiro)

    assert guerreiro.vida == 120


def test_pocao_de_vida_com_vida_cheia_nao_e_usada():
    guerreiro = Guerreiro("Arthur")

    assert PocaoVida().usar(guerreiro) is False


def test_pocao_de_mana_recupera_mana():
    mago = Mago("Merlin")
    mago.mana = 40

    usado = PocaoMana("Poção de Mana", 30).usar(mago)

    assert usado is True
    assert mago.mana == 70


def test_pocao_de_mana_sem_efeito_no_guerreiro():
    guerreiro = Guerreiro("Arthur")

    assert PocaoMana("Poção de Mana", 30).usar(guerreiro) is False


def test_pocao_de_vida_tem_valores_padrao():
    pocao = PocaoVida()

    assert pocao.nome == "Poção de Vida"
    assert pocao.valor == 40


def test_item_base_exige_implementacao_de_usar():
    with pytest.raises(NotImplementedError):
        Item("Genérico", 1).usar(Guerreiro("Arthur"))


def test_aljava_repoe_flechas_sem_passar_do_maximo():
    arqueiro = Arqueiro("Robin")
    arqueiro.flechas = 4

    assert Aljava().usar(arqueiro) is True
    assert arqueiro.flechas == 10

    Aljava().usar(arqueiro)
    assert arqueiro.flechas == Arqueiro.FLECHAS_MAXIMAS


def test_aljava_com_flechas_cheias_ou_sem_arco_nao_e_usada():
    assert Aljava().usar(Arqueiro("Robin")) is False
    assert Aljava().usar(Guerreiro("Arthur")) is False
