from models.pessoa import Pessoa
from utils.permissoes import Permissao

class Usuario(Pessoa):
    def __init__(self, nome, matricula, senha):
        super().__init__(nome, matricula, senha)
        self.emprestimos = []

    def tem_permissao(self, permissao: Permissao) -> bool:
        return permissao == Permissao.LISTAR_LIVROS