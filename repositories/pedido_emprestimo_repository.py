class PedidoEmprestimoRepository:
    def solicitar(self, usuario_id, livro_id):
        raise NotImplementedError

    def listar_pendentes(self):
        raise NotImplementedError

    def listar_por_usuario(self, usuario_id):
        raise NotImplementedError

    def aceitar(self, pedido_id, bibliotecario_id, data_prevista_devolucao):
        raise NotImplementedError
