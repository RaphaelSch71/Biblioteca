class EmprestimoRepository:
    def salvar(self, emprestimo):
        raise NotImplementedError

    def listar(self):
        raise NotImplementedError

    def listar_ativos(self):
        raise NotImplementedError

    def buscar_por_id(self, emprestimo_id):
        raise NotImplementedError

    def atualizar(self, emprestimo):
        raise NotImplementedError

    def remover(self, emprestimo_id):
        raise NotImplementedError