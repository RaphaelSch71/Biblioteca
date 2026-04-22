from models.pessoa import Pessoa

class Funcionario(Pessoa):
    def __init__(self, nome: str, matricula: str, senha: str | None = None):
        super().__init__(nome, matricula, senha)

    def tem_permissao(self, permissao):
        return False