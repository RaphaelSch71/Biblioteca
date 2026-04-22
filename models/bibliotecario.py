from models.funcionario import Funcionario
from utils.permissoes import Permissao

class Bibliotecario(Funcionario):
    def __init__(self, nome, matricula, senha=None):
        super().__init__(nome, matricula, senha)
        self.permissoes = {
            Permissao.CADASTRAR_LIVRO,
            Permissao.REMOVER_LIVRO,
            Permissao.REALIZAR_EMPRESTIMO,
            Permissao.DEVOLVER_LIVRO,
            Permissao.LISTAR_LIVROS,
            Permissao.GERENCIAR_USUARIOS,
            Permissao.GERENCIAR_EMPRESTIMOS,
        }

    def tem_permissao(self, permissao):
        return permissao in self.permissoes