class LivroRepository:
    def salvar(self, livro):
        raise NotImplementedError

    def listar(self):
        raise NotImplementedError

    def buscar_por_isbn(self, isbn):
        raise NotImplementedError

    def buscar_por_id(self, livro_id):
        raise NotImplementedError

    def atualizar(self, livro):
        raise NotImplementedError

    def remover(self, livro_id):
        raise NotImplementedError