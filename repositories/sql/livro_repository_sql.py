from models.livro import Livro
from repositories.base_repository import BaseRepository
from repositories.livro_repository import LivroRepository


class LivroRepositorySQL(BaseRepository, LivroRepository):
    def __init__(self):
        super().__init__()

    def salvar(self, livro: Livro):
        row = self._execute(
            "EXEC dbo.usp_CadastrarLivro @Titulo=?, @Autor=?, @ISBN=?, @AnoPublicacao=?",
            (livro.titulo, livro.autor, livro.isbn, livro.ano_publicacao),
            fetch="one",
            commit=True,
        )
        if row:
            livro.id = int(row[0])
        livro.disponivel = True
        return livro

    def listar(self):
        rows = self._execute("EXEC dbo.usp_ListarLivros", fetch="all")
        livros = []
        for row in rows:
            livro = Livro(row[0], row[1], row[2], row[3], row[4])
            livro.disponivel = bool(row[5])
            livros.append(livro)
        return livros

    def buscar_por_isbn(self, isbn):
        row = self._execute("EXEC dbo.usp_ObterLivroPorISBN @ISBN=?", (isbn,), fetch="one")
        if not row:
            return None

        livro = Livro(row[0], row[1], row[2], row[3], row[4])
        livro.disponivel = bool(row[5])
        return livro

    def buscar_por_id(self, livro_id):
        row = self._execute("EXEC dbo.usp_ObterLivroPorId @Id=?", (livro_id,), fetch="one")
        if not row:
            return None

        livro = Livro(row[0], row[1], row[2], row[3], row[4])
        livro.disponivel = bool(row[5])
        return livro

    def atualizar(self, livro):
        self._execute(
            "EXEC dbo.usp_AtualizarLivro @Id=?, @Titulo=?, @Autor=?, @ISBN=?, @AnoPublicacao=?",
            (livro.id, livro.titulo, livro.autor, livro.isbn, livro.ano_publicacao),
            commit=True,
        )
        return livro

    def remover(self, livro_id):
        self._execute("EXEC dbo.usp_RemoverLivro @Id=?", (livro_id,), commit=True)
        return True
