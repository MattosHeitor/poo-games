from src.batalha import Batalha
from src.guerreiro import Guerreiro
from src.inimigo import Inimigo
from src.arqueiro import Arqueiro
from src.chefe_final import ChefeFinal
from src.item import PocaoVida
from src.mago import Mago


def simular_entradas(monkeypatch, entradas):
    """Faz o input() devolver, em ordem, os valores da lista."""
    iterador = iter(entradas)
    monkeypatch.setattr("builtins.input", lambda _="": next(iterador))


def test_vitoria_do_jogador(monkeypatch):
    simular_entradas(monkeypatch, ["1"])
    goblin = Inimigo("Goblin", vida=10, ataque=15, defesa=5)
    jogador = Guerreiro("Arthur")

    resultado = Batalha(jogador, goblin).iniciar()

    assert resultado == "vitoria"
    assert goblin.esta_vivo() is False
    assert jogador.vida == jogador.vida_maxima  # inimigo morto não contra-ataca


def test_derrota_do_jogador(monkeypatch):
    simular_entradas(monkeypatch, ["1"])
    orc = Inimigo("Orc", vida=500, ataque=100, defesa=0)
    jogador = Guerreiro("Arthur")
    jogador.vida = 50  # um único golpe do orc (100 - 15 = 85) é fatal

    assert Batalha(jogador, orc).iniciar() == "derrota"
    assert jogador.esta_vivo() is False


def test_fugir_encerra_a_batalha(monkeypatch):
    simular_entradas(monkeypatch, ["3"])
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    assert Batalha(Guerreiro("Arthur"), goblin).iniciar() == "fuga"
    assert goblin.vida == 100


def test_opcao_invalida_nao_gasta_turno(monkeypatch):
    simular_entradas(monkeypatch, ["9", "abc", "3"])
    jogador = Guerreiro("Arthur")
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    Batalha(jogador, goblin).iniciar()

    assert jogador.vida == jogador.vida_maxima


def test_inimigo_contra_ataca_apos_o_jogador(monkeypatch):
    simular_entradas(monkeypatch, ["1", "3"])
    jogador = Guerreiro("Arthur")  # defesa 15
    goblin = Inimigo("Goblin", vida=100, ataque=30, defesa=5)

    Batalha(jogador, goblin).iniciar()

    assert goblin.vida == 85     # 20 - 5
    assert jogador.vida == 105   # 30 - 15


def test_usar_item_cura_e_consome_o_item(monkeypatch):
    simular_entradas(monkeypatch, ["2", "1", "3"])
    jogador = Guerreiro("Arthur")
    jogador.vida = 50
    jogador.adicionar_item(PocaoVida())
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    Batalha(jogador, goblin).iniciar()

    # curou 40 (50 -> 90) e o goblin contra-atacou 1 (defesa 15 vs ataque 15 -> mínimo 1)
    assert jogador.vida == 89
    assert jogador.inventario == []


def test_usar_item_sem_inventario_nao_gasta_turno(monkeypatch):
    simular_entradas(monkeypatch, ["2", "3"])
    jogador = Guerreiro("Arthur")
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    Batalha(jogador, goblin).iniciar()

    assert jogador.vida == jogador.vida_maxima


def test_voltar_do_inventario_mantem_item_e_turno(monkeypatch):
    simular_entradas(monkeypatch, ["2", "0", "3"])
    jogador = Guerreiro("Arthur")
    jogador.vida = 50
    jogador.adicionar_item(PocaoVida())
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    Batalha(jogador, goblin).iniciar()

    assert jogador.vida == 50
    assert len(jogador.inventario) == 1


def test_mago_usa_magia_na_batalha(monkeypatch):
    simular_entradas(monkeypatch, ["4", "3"])
    mago = Mago("Merlin")
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    Batalha(mago, goblin).iniciar()

    assert goblin.vida == 55  # magia de 45 ignora defesa
    assert mago.mana == 80


def test_magia_sem_mana_nao_gasta_turno(monkeypatch):
    simular_entradas(monkeypatch, ["4", "3"])
    mago = Mago("Merlin")
    mago.mana = 0
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    Batalha(mago, goblin).iniciar()

    assert goblin.vida == 100
    assert mago.vida == mago.vida_maxima


def test_guerreiro_nao_tem_opcao_de_magia(monkeypatch):
    simular_entradas(monkeypatch, ["4", "3"])
    jogador = Guerreiro("Arthur")
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    Batalha(jogador, goblin).iniciar()

    assert jogador.vida == jogador.vida_maxima  # "4" foi tratada como inválida


def test_arqueiro_usa_tiro_certeiro_na_batalha(monkeypatch, capsys):
    simular_entradas(monkeypatch, ["4", "3"])
    arqueiro = Arqueiro("Robin")  # tiro = int(22 * 1.5) = 33
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    Batalha(arqueiro, goblin).iniciar()

    assert "4 - Tiro certeiro" in capsys.readouterr().out
    assert goblin.vida == 72     # 33 - 5
    assert arqueiro.flechas == 10


def test_tiro_certeiro_sem_flechas_nao_gasta_turno(monkeypatch):
    simular_entradas(monkeypatch, ["4", "3"])
    arqueiro = Arqueiro("Robin")
    arqueiro.flechas = 1
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    Batalha(arqueiro, goblin).iniciar()

    assert goblin.vida == 100
    assert arqueiro.vida == arqueiro.vida_maxima


def test_menu_mostra_habilidade_so_para_quem_possui(monkeypatch, capsys):
    simular_entradas(monkeypatch, ["3", "3"])
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    Batalha(Guerreiro("Arthur"), goblin).iniciar()
    Batalha(Mago("Merlin"), goblin).iniciar()
    saida = capsys.readouterr().out

    assert saida.count("4 - ") == 1          # só o Mago
    assert "4 - Usar magia" in saida


def test_batalha_contra_chefe_final_termina_em_vitoria(monkeypatch):
    # Mago: 5 magias ganham do chefe (160 de vida) se a vida for suficiente.
    simular_entradas(monkeypatch, ["4"] * 4)
    mago = Mago("Merlin")
    chefe = ChefeFinal()

    assert Batalha(mago, chefe).iniciar() == "vitoria"
    assert chefe.esta_vivo() is False
    assert mago.esta_vivo() is True
