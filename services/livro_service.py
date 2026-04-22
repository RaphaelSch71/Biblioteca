from models.livro import Livro

class LivroService:
    def __init__(self, livro_repository=None):
        self.livros = []
        self.repo = livro_repository
        self.proximo_id = 1

    def cadastrar_livro(self, titulo, autor, isbn, ano_publicacao=None):
        if not titulo or not autor or not isbn:
            raise ValueError("Título, autor e ISBN são obrigatórios")

        livro = Livro(
            id=None,
            titulo=titulo,
            autor=autor,
            isbn=isbn,
            ano_publicacao=ano_publicacao
        )

        if self.repo is not None:
            if hasattr(self.repo, "cadastrar_livro"):
                self.repo.cadastrar_livro(livro)
            else:
                self.repo.salvar(livro)
        else:
            self.livros.append(livro)

        return livro

    def listar_livros(self):
        if self.repo is not None:
            return self.repo.listar()

        return list(self.livros)

    def listar_Livros(self):
        return self.listar_livros()