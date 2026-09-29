class Batalha:
    """Batalha por turnos em modo texto entre um jogador e um inimigo."""

    def __init__(self, jogador, inimigo):
        self.jogador = jogador
        self.inimigo = inimigo

    # ------------------------------------------------------------------
    # Interface (apenas print/input)
    # ------------------------------------------------------------------
    def _mostrar_status(self):
        print("\n" + "-" * 60)
        self.jogador.mostrar_status()
        self.inimigo.mostrar_status()
        print("-" * 60)

    def _tem_magia(self):
        # Duck typing: qualquer personagem com usar_magia ganha a opção 4.
        return hasattr(self.jogador, "usar_magia")

    def _mostrar_menu(self):
        print("\n--- AÇÕES ---")
        print("1 - Atacar")
        print("2 - Usar item")
        print("3 - Fugir")
        if self._tem_magia():
            print("4 - Usar magia")

    # ------------------------------------------------------------------
    # Ações do jogador (devolvem True se o turno foi gasto)
    # ------------------------------------------------------------------
    def _usar_item(self):
        inventario = self.jogador.inventario

        if not inventario:
            print("Você não possui itens.")
            return False

        print("\n--- INVENTÁRIO ---")
        for i, item in enumerate(inventario, start=1):
            print(f"{i} - {item.nome} ({item.valor})")
        print("0 - Voltar")

        escolha = input("Escolha um item: ").strip()

        if not escolha.isdigit() or not (0 <= int(escolha) <= len(inventario)):
            print("Opção inválida.")
            return False

        if escolha == "0":
            return False

        item = inventario[int(escolha) - 1]

        # O item só é consumido (e o turno gasto) se teve efeito.
        if item.usar(self.jogador):
            inventario.remove(item)
            return True
        return False

    def _usar_magia(self):
        if not self.jogador.pode_usar_magia():
            print("O mago não possui mana suficiente.")
            return False

        self.jogador.usar_magia(self.inimigo)
        return True

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    def iniciar(self):
        """Executa a batalha e devolve "vitoria", "derrota" ou "fuga"."""

        print("=" * 60)
        print("                    INÍCIO DA BATALHA")
        print(f"              {self.jogador.nome}  VS  {self.inimigo.nome}")
        print("=" * 60)

        while self.jogador.esta_vivo() and self.inimigo.esta_vivo():

            self._mostrar_status()
            self._mostrar_menu()

            opcao = input("Escolha uma opção: ").strip()
            print()

            if opcao == "1":
                self.jogador.atacar(self.inimigo)
                gastou_turno = True

            elif opcao == "2":
                gastou_turno = self._usar_item()

            elif opcao == "3":
                print("Você fugiu da batalha!")
                return "fuga"

            elif opcao == "4" and self._tem_magia():
                gastou_turno = self._usar_magia()

            else:
                print("Opção inválida.")
                continue

            # Ações sem efeito (ex.: sem itens, sem mana) não gastam o turno.
            # O inimigo só contra-ataca se ainda estiver vivo.
            if gastou_turno and self.inimigo.esta_vivo():
                self.inimigo.atacar(self.jogador)

        return self._anunciar_resultado()

    def _anunciar_resultado(self):
        print("\n" + "=" * 60)
        if self.jogador.esta_vivo():
            print(f"VITÓRIA! {self.inimigo.nome} foi derrotado!")
            resultado = "vitoria"
        else:
            print(f"DERROTA... {self.jogador.nome} foi derrotado por {self.inimigo.nome}.")
            resultado = "derrota"
        print("=" * 60)
        return resultado
