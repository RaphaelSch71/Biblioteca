from models.usuario import Usuario
from models.bibliotecario import Bibliotecario
from repositories.base_repository import BaseRepository
from repositories.usuario_repository import UsuarioRepository


class UsuarioRepositorySQL(BaseRepository, UsuarioRepository):
    def __init__(self):
        super().__init__()

    def salvar(self, usuario):
        tipo = "bibliotecario" if isinstance(usuario, Bibliotecario) else "usuario"
        row = self._execute(
            "EXEC dbo.usp_CadastrarUsuario @Nome=?, @Matricula=?, @Senha=?, @Tipo=?",
            (usuario.nome, usuario.matricula, usuario.senha, tipo),
            fetch="one",
            commit=True,
        )
        if row:
            usuario.id = int(row[0])
        return usuario

    def listar(self):
        rows = self._execute("EXEC dbo.usp_ListarUsuarios", fetch="all")
        usuarios = []
        for row in rows:
            usuario = self._to_usuario_model(row)
            usuarios.append(usuario)
        return usuarios

    def buscar_por_matricula(self, matricula):
        row = self._execute(
            "EXEC dbo.usp_ObterUsuarioPorMatricula @Matricula=?",
            (matricula,),
            fetch="one",
        )
        if not row:
            return None
        return self._to_usuario_model(row, has_senha=True)

    def buscar_por_id(self, usuario_id):
        row = self._execute("EXEC dbo.usp_ObterUsuarioPorId @Id=?", (usuario_id,), fetch="one")
        if not row:
            return None
        return self._to_usuario_model(row, has_senha=False)

    def atualizar(self, usuario):
        tipo = "bibliotecario" if isinstance(usuario, Bibliotecario) else "usuario"
        ativo = int(getattr(usuario, "ativo", True))
        self._execute(
            "EXEC dbo.usp_AtualizarUsuario @Id=?, @Nome=?, @Matricula=?, @Senha=?, @Tipo=?, @Ativo=?",
            (usuario.id, usuario.nome, usuario.matricula, usuario.senha, tipo, ativo),
            commit=True,
        )
        return usuario

    def remover(self, usuario_id):
        self._execute("EXEC dbo.usp_RemoverUsuario @Id=?", (usuario_id,), commit=True)
        return True

    @staticmethod
    def _to_usuario_model(row, has_senha=False):
        # Row esperado:
        # Com senha: Id, Nome, Matricula, Senha, Tipo, Ativo, DataCadastro
        # Sem senha: Id, Nome, Matricula, Tipo, Ativo, DataCadastro
        if has_senha:
            user_id, nome, matricula, senha, tipo, ativo, _ = row
        else:
            user_id, nome, matricula, tipo, ativo, _ = row
            senha = ""

        if str(tipo) == "bibliotecario":
            usuario = Bibliotecario(nome, matricula, senha)
        else:
            usuario = Usuario(nome, matricula, senha)

        usuario.id = int(user_id)
        usuario.ativo = bool(ativo)
        return usuario
