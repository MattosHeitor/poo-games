from src.chefe_final import ChefeFinal
from src.guerreiro import Guerreiro
from src.inimigo import Inimigo
from src.vampiro import Vampiro


# ---------- Inimigo comum ----------

def test_inimigo_comum_ataca():
    goblin = Inimigo("Goblin", vida=100, ataque=30, defesa=5)
    guerreiro = Guerreiro("Arthur")

    assert goblin.atacar(guerreiro) == 15
    assert guerreiro.vida == 105


# ---------- Vampiro (novo tipo de inimigo) ----------

def test_vampiro_causa_dano_e_se_cura():
    vampiro = Vampiro()          # ataque 22
    guerreiro = Guerreiro("Arthur")  # defesa 15 -> dano 7
    vampiro.receber_dano(28)     # 28 - 8 = 20 -> vida 70

    vampiro.atacar(guerreiro)

    assert guerreiro.vida == 113
    assert vampiro.vida == 73    # curou 7 // 2 = 3


def test_vampiro_nao_ultrapassa_a_vida_maxima():
    vampiro = Vampiro()
    guerreiro = Guerreiro("Arthur")

    vampiro.atacar(guerreiro)

    assert vampiro.vida == vampiro.vida_maxima == 90


# ---------- Chefe final ----------

def test_chefe_final_e_mais_forte_que_um_inimigo_comum():
    chefe = ChefeFinal()

    assert chefe.nome == "Lorde Sombrio"
    assert chefe.vida > 150


def test_chefe_final_desfere_golpe_devastador_a_cada_tres_ataques():
    chefe = ChefeFinal()             # ataque 22 -> golpe devastador 33
    guerreiro = Guerreiro("Arthur")  # defesa 15

    danos = [chefe.atacar(guerreiro) for _ in range(3)]

    assert danos == [7, 7, 18]       # 22-15, 22-15, 33-15


def test_chefe_final_repete_o_ciclo_de_golpes():
    chefe = ChefeFinal()
    guerreiro = Guerreiro("Arthur")
    guerreiro.vida = guerreiro.vida_maxima = 1000

    danos = [chefe.atacar(guerreiro) for _ in range(6)]

    assert danos == [7, 7, 18, 7, 7, 18]
