from models.emprestimo import Emprestimo
from models.livro import Livro
from models.usuario import Usuario
from repositories.base_repository import BaseRepository
from repositories.emprestimo_repository import EmprestimoRepository


class EmprestimoRepositorySQL(BaseRepository, EmprestimoRepository):
    def __init__(self):
        super().__init__()

    def salvar(self, emprestimo):
        row = self._execute(
            "EXEC dbo.usp_RealizarEmprestimo @LivroId=?, @UsuarioId=?",
            (emprestimo.livro.id, emprestimo.usuario.id),
            fetch="one",
            commit=True,
        )

        if row:
            emprestimo.id = int(row[0])

        emprestimo.livro.disponivel = False
        emprestimo.ativo = True
        return emprestimo

    def realizar_emprestimo(self, livro, usuario):
        emprestimo = Emprestimo(livro, usuario)
        return self.salvar(emprestimo)

    def devolver_emprestimo(self, emprestimo):
        if getattr(emprestimo, "id", None) is None:
            raise ValueError("Empréstimo sem ID. Não é possível devolver no banco.")

        self._execute(
            "EXEC dbo.usp_DevolverLivro @EmprestimoId=?",
            (emprestimo.id,),
            commit=True,
        )

        emprestimo.devolver()
        return emprestimo

    def listar(self):
        rows = self._execute("EXEC dbo.usp_ListarEmprestimos", fetch="all")
        return [self._row_to_emprestimo(row) for row in rows]

    def listar_por_usuario(self, usuario_id):
        emprestimos = self.listar()
        return [e for e in emprestimos if getattr(e.usuario, "id", None) == int(usuario_id)]

    def listar_ativos(self):
        emprestimos = self.listar()
        return [e for e in emprestimos if e.ativo]

    def buscar_por_id(self, emprestimo_id):
        row = self._execute("EXEC dbo.usp_ObterEmprestimoPorId @Id=?", (emprestimo_id,), fetch="one")
        if not row:
            return None
        return self._row_to_emprestimo(row)

    def atualizar(self, emprestimo):
        self._execute(
            "EXEC dbo.usp_AtualizarEmprestimo @Id=?, @DataEmprestimo=?, @DataDevolucao=?, @Ativo=?",
            (
                emprestimo.id,
                emprestimo.data_emprestimo,
                emprestimo.data_devolucao,
                int(emprestimo.ativo),
            ),
            commit=True,
        )
        return emprestimo

    def remover(self, emprestimo_id):
        self._execute("EXEC dbo.usp_RemoverEmprestimo @Id=?", (emprestimo_id,), commit=True)
        return True

    def _row_to_emprestimo(self, row):
        # Row: Id, LivroId, Titulo, ISBN, UsuarioId, NomeUsuario, Matricula, DataEmprestimo, DataDevolucao, Ativo
        livro = Livro(row[1], row[2], "", row[3], None)
        livro.disponivel = not bool(row[9])

        usuario = Usuario(row[5], row[6], "")
        usuario.id = int(row[4])

        emprestimo = Emprestimo(livro, usuario)
        emprestimo.id = int(row[0])
        emprestimo.data_emprestimo = row[7]
        emprestimo.data_devolucao = row[8]
        emprestimo.ativo = bool(row[9])
        return emprestimo
