from repositories.base_repository import BaseRepository
from repositories.pedido_emprestimo_repository import PedidoEmprestimoRepository


class PedidoEmprestimoRepositorySQL(BaseRepository, PedidoEmprestimoRepository):
    def solicitar(self, usuario_id, livro_id):
        row = self._execute(
            "EXEC dbo.usp_SolicitarPedidoEmprestimo @UsuarioId=?, @LivroId=?",
            (usuario_id, livro_id),
            fetch="one",
            commit=True,
        )
        return int(row[0]) if row else None

    def listar_pendentes(self):
        rows = self._execute("EXEC dbo.usp_ListarPedidosEmprestimoPendentes", fetch="all")
        result = []
        for r in rows:
            result.append(
                {
                    "id": int(r[0]),
                    "usuario_id": int(r[1]),
                    "usuario_nome": r[2],
                    "usuario_matricula": r[3],
                    "livro_id": int(r[4]),
                    "livro_titulo": r[5],
                    "livro_isbn": r[6],
                    "status": r[7],
                    "data_pedido": r[8],
                }
            )
        return result

    def listar_por_usuario(self, usuario_id):
        rows = self._execute(
            "EXEC dbo.usp_ListarPedidosEmprestimoPorUsuario @UsuarioId=?",
            (usuario_id,),
            fetch="all",
        )
        result = []
        for r in rows:
            result.append(
                {
                    "id": int(r[0]),
                    "livro_id": int(r[1]),
                    "livro_titulo": r[2],
                    "livro_isbn": r[3],
                    "status": r[4],
                    "data_pedido": r[5],
                    "data_prevista_devolucao": r[6],
                    "bibliotecario_nome": r[7],
                    "bibliotecario_matricula": r[8],
                    "emprestimo_id": r[9],
                }
            )
        return result

    def aceitar(self, pedido_id, bibliotecario_id, data_prevista_devolucao):
        row = self._execute(
            "EXEC dbo.usp_AceitarPedidoEmprestimo @PedidoId=?, @BibliotecarioId=?, @DataPrevistaDevolucao=?",
            (pedido_id, bibliotecario_id, data_prevista_devolucao),
            fetch="one",
            commit=True,
        )
        return int(row[0]) if row else None
