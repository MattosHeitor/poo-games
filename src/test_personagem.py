from src.guerreiro import Guerreiro
from src.inimigo import Inimigo
from src.mago import Mago


def test_guerreiro_esta_vivo():

    guerreiro = Guerreiro("Arthur")

    assert guerreiro.esta_vivo() is True


# ---------- Issue #1: receber_dano ----------

def test_personagem_recebe_dano():
    guerreiro = Guerreiro("Arthur")  # vida 120, defesa 15

    dano = guerreiro.receber_dano(25)

    assert dano == 10
    assert guerreiro.vida == 110


def test_dano_minimo_e_um():
    guerreiro = Guerreiro("Arthur")  # defesa 15

    guerreiro.receber_dano(5)  # menor que a defesa

    assert guerreiro.vida == 119


def test_personagem_morre():
    goblin = Inimigo("Goblin", vida=10, ataque=15, defesa=5)

    goblin.receber_dano(100)

    assert goblin.vida == 0  # vida nunca fica negativa
    assert goblin.esta_vivo() is False


# ---------- Issue #2: ataque do Guerreiro ----------

def test_guerreiro_ataca():
    guerreiro = Guerreiro("Arthur")  # ataque 20
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    guerreiro.atacar(goblin)

    assert goblin.vida == 85  # 20 - 5 de defesa = 15


# ---------- Issue #3: ataque do Inimigo ----------

def test_inimigo_ataca():
    goblin = Inimigo("Goblin", vida=100, ataque=30, defesa=5)
    guerreiro = Guerreiro("Arthur")  # defesa 15

    goblin.atacar(guerreiro)

    assert guerreiro.vida == 105  # 30 - 15 = 15


# ---------- Issue #4: ataque do Mago ----------

def test_mago_ataca():
    mago = Mago("Merlin")  # ataque 30 -> ataque normal 15
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)

    mago.atacar(goblin)

    assert goblin.vida == 90  # 15 - 5 = 10


def test_mago_recupera_mana_ao_atacar_sem_passar_do_maximo():
    mago = Mago("Merlin")
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)
    mago.mana = 50

    mago.atacar(goblin)
    assert mago.mana == 60

    mago.mana = 100
    mago.atacar(goblin)
    assert mago.mana == 100


# ---------- Issue #5: magia do Mago ----------

def test_mago_usa_magia_ignora_defesa_e_gasta_mana():
    mago = Mago("Merlin")  # ataque 30 -> magia 45
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=50)

    mago.usar_magia(goblin)

    assert goblin.vida == 55  # 45 de dano, defesa ignorada
    assert mago.mana == 80


def test_mago_sem_mana_nao_usa_magia():
    mago = Mago("Merlin")
    goblin = Inimigo("Goblin", vida=100, ataque=15, defesa=5)
    mago.mana = 10  # menor que o custo da magia

    mago.usar_magia(goblin)

    assert goblin.vida == 100
    assert mago.mana == 10


# ---------- Cura e inventário ----------

def test_curar_nao_ultrapassa_vida_maxima():
    guerreiro = Guerreiro("Arthur")  # vida máxima 120
    guerreiro.receber_dano(35)       # 35 - 15 = 20 de dano -> vida 100

    curado = guerreiro.curar(50)

    assert curado == 20
    assert guerreiro.vida == 120


def test_adicionar_item_ao_inventario():
    guerreiro = Guerreiro("Arthur")

    guerreiro.adicionar_item("qualquer-item")

    assert len(guerreiro.inventario) == 1

