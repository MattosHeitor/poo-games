# Adiciona src/ ao sys.path para que os módulos de src/ possam importar
# uns aos outros (ex.: "from personagem import Personagem") durante os testes.
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))   
