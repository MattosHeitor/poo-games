"""Estados que duram mais de um turno: veneno e paralisia.

Os estados são guardados como atributos no próprio personagem:
- veneno_dano e veneno_turnos: dano por turno e quantos turnos faltam.
- paralisado: True quando o personagem vai perder a próxima vez.
"""


def envenenar(alvo, dano_por_turno, turnos):
    alvo.veneno_dano = dano_por_turno
    alvo.veneno_turnos = turnos


def esta_envenenado(personagem):
    return getattr(personagem, "veneno_turnos", 0) > 0


def sofrer_veneno(personagem):
    """Aplica o dano do veneno no começo do turno e devolve o dano.

    O veneno tira vida direto (não passa pela defesa, escudo ou esquiva).
    """
    if not esta_envenenado(personagem):
        return 0

    dano = min(personagem.vida, personagem.veneno_dano)
    personagem.vida -= dano
    personagem.veneno_turnos -= 1

    print(
        f"{personagem.nome} sofreu {dano} de dano do veneno! "
        f"(turnos restantes: {personagem.veneno_turnos})"
    )

    # O esqueleto pode se levantar mesmo morrendo pelo veneno
    if personagem.vida == 0 and hasattr(personagem, "tentar_renascer"):
        personagem.tentar_renascer()

    return dano


def paralisar(alvo):
    alvo.paralisado = True


def esta_paralisado(personagem):
    return getattr(personagem, "paralisado", False)
