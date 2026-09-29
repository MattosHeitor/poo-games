# ⚔️ Jogo de Batalha

Projeto desenvolvido na disciplina de Programação Orientada a Objetos.

Jogo de batalha por turnos com interface apenas de texto (`print` / `input`).
O jogador escolhe uma classe (Guerreiro ou Mago), escolhe um inimigo e luta
usando ataques, itens e, no caso do Mago, magias.

## Executando o projeto

Na raiz do projeto:

```bash
pip install -r requirements.txt   # instala o pytest
python src/main.py                # inicia o jogo
pytest                            # roda os testes
```

## Fluxo de desenvolvimento

Cada funcionalidade deve ser desenvolvida em uma branch própria.

Exemplo:

feature/ataque-guerreiro

Depois:

```bash
git add .
git commit -m "feat: implementa ataque do guerreiro"
git push
```

Após o push, abra um Pull Request no GitHub.

Regras:
- Não desenvolver diretamente na branch main.
- Cada funcionalidade deve possuir uma issue.
- Cada issue deve ser desenvolvida em uma branch.
- O Pull Request deve ser revisado por outro aluno.
- O código deve passar pelos testes antes do merge.
