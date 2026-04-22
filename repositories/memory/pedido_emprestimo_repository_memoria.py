from datetime import datetime

from repositories.pedido_emprestimo_repository import PedidoEmprestimoRepository


class PedidoEmprestimoRepositoryMemoria(PedidoEmprestimoRepository):
    def __init__(self, livro_repo=None):
        self._pedidos = []
        self._next_id = 1
        self._next_emprestimo = 1
        self.livro_repo = livro_repo

    def solicitar(self, usuario_id, livro_id):
        pedido = {
            "id": self._next_id,
            "usuario_id": int(usuario_id),
            "usuario_nome": "",
            "usuario_matricula": "",
            "livro_id": int(livro_id),
            "livro_titulo": "",
            "livro_isbn": "",
            "status": "PENDENTE",
            "data_pedido": datetime.now(),
            "data_prevista_devolucao": None,
            "bibliotecario_nome": None,
            "bibliotecario_matricula": None,
            "emprestimo_id": None,
        }
        self._next_id += 1
        self._pedidos.append(pedido)
        return pedido["id"]

    def listar_pendentes(self):
        return [p for p in self._pedidos if p["status"] == "PENDENTE"]

    def listar_por_usuario(self, usuario_id):
        return [p for p in self._pedidos if p["usuario_id"] == int(usuario_id)]

    def aceitar(self, pedido_id, bibliotecario_id, data_prevista_devolucao):
        pedido = next((p for p in self._pedidos if p["id"] == int(pedido_id)), None)
        if pedido is None:
            raise ValueError("Pedido não encontrado.")
        if pedido["status"] != "PENDENTE":
            raise ValueError("Pedido já processado.")

        pedido["status"] = "ACEITO"
        pedido["data_prevista_devolucao"] = data_prevista_devolucao
        pedido["bibliotecario_nome"] = f"Biblio {bibliotecario_id}"
        pedido["bibliotecario_matricula"] = str(bibliotecario_id)
        pedido["emprestimo_id"] = self._next_emprestimo
        self._next_emprestimo += 1

        if self.livro_repo is not None:
            livro = self.livro_repo.buscar_por_id(pedido["livro_id"])
            if livro is not None:
                livro.disponivel = False

        return pedido["emprestimo_id"]
