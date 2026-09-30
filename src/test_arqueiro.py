from src.arqueiro import Arqueiro
from src.inimigo import Inimigo


def novo_alvo():
    return Inimigo("Goblin", vida=100, ataque=15, defesa=5)


def test_atributos_iniciais_do_arqueiro():
    arqueiro = Arqueiro("Robin")

    assert (arqueiro.vida, arqueiro.ataque, arqueiro.defesa) == (100, 22, 8)
    assert arqueiro.flechas == 12
    assert arqueiro.esta_vivo() is True


def test_arqueiro_ataca_e_gasta_uma_flecha():
    arqueiro, alvo = Arqueiro("Robin"), novo_alvo()

    arqueiro.atacar(alvo)

    assert alvo.vida == 83        # 22 - 5
    assert arqueiro.flechas == 11


def test_arqueiro_sem_flechas_ataca_com_adaga():
    arqueiro, alvo = Arqueiro("Robin"), novo_alvo()
    arqueiro.flechas = 0

    arqueiro.atacar(alvo)

    assert alvo.vida == 98        # 22 // 3 = 7 -> 7 - 5 = 2
    assert arqueiro.flechas == 0


def test_tiro_certeiro_causa_mais_dano_e_gasta_flechas():
    arqueiro, alvo = Arqueiro("Robin"), novo_alvo()

    arqueiro.tiro_certeiro(alvo)

    assert alvo.vida == 72        # int(22 * 1.5) = 33 -> 33 - 5 = 28
    assert arqueiro.flechas == 10


def test_tiro_certeiro_sem_flechas_suficientes_nao_faz_nada():
    arqueiro, alvo = Arqueiro("Robin"), novo_alvo()
    arqueiro.flechas = 1

    assert arqueiro.pode_usar_habilidade() is False
    assert arqueiro.tiro_certeiro(alvo) == 0
    assert alvo.vida == 100
    assert arqueiro.flechas == 1


def test_recuperar_flechas_respeita_o_maximo():
    arqueiro = Arqueiro("Robin")
    arqueiro.flechas = 10

    assert arqueiro.recuperar_flechas(6) == 2
    assert arqueiro.flechas == 12


def test_status_do_arqueiro_mostra_flechas(capsys):
    Arqueiro("Robin").mostrar_status()

    assert "Flechas: 12/12" in capsys.readouterr().out
