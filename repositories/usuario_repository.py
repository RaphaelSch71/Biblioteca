class UsuarioRepository:
    def salvar(self, usuario):
        raise NotImplementedError

    def listar(self):
        raise NotImplementedError

    def buscar_por_matricula(self, matricula):
        raise NotImplementedError

    def buscar_por_id(self, usuario_id):
        raise NotImplementedError

    def atualizar(self, usuario):
        raise NotImplementedError

    def remover(self, usuario_id):
        raise NotImplementedError