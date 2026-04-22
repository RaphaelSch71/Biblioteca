from repositories.livro_repository import LivroRepository

class LivroRepositoryMemoria(LivroRepository):
    def __init__(self):
        self.livros = []
        self._proximo_id = 1

    def salvar(self, livro):
        if getattr(livro, "id", None) is None:
            livro.id = self._proximo_id
            self._proximo_id += 1
        self.livros.append(livro)
        return livro

    def listar(self):
        return self.livros

    def buscar_por_isbn(self, isbn):
        for livro in self.livros:
            if livro.isbn == isbn:
                return livro
        return None

    def buscar_por_id(self, livro_id):
        for livro in self.livros:
            if getattr(livro, "id", None) == livro_id:
                return livro
        return None

    def atualizar(self, livro):
        for i, existente in enumerate(self.livros):
            if getattr(existente, "id", None) == getattr(livro, "id", None):
                self.livros[i] = livro
                return livro
        return None

    def remover(self, livro_id):
        livro = self.buscar_por_id(livro_id)
        if livro is None:
            return False
        self.livros.remove(livro)
        return True