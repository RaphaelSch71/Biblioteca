from repositories.usuario_repository import UsuarioRepository

class UsuarioRepositoryMemoria(UsuarioRepository):
    def __init__(self):
        self.usuarios = []
        self._proximo_id = 1

    def salvar(self, usuario):
        if getattr(usuario, "id", None) is None:
            usuario.id = self._proximo_id
            self._proximo_id += 1
        self.usuarios.append(usuario)
        return usuario

    def listar(self):
        return self.usuarios

    def buscar_por_matricula(self, matricula):
        for usuario in self.usuarios:
            if usuario.matricula == matricula:
                return usuario
        return None

    def buscar_por_id(self, usuario_id):
        for usuario in self.usuarios:
            if getattr(usuario, "id", None) == usuario_id:
                return usuario
        return None

    def atualizar(self, usuario):
        for i, existente in enumerate(self.usuarios):
            if getattr(existente, "id", None) == getattr(usuario, "id", None):
                self.usuarios[i] = usuario
                return usuario
        return None

    def remover(self, usuario_id):
        usuario = self.buscar_por_id(usuario_id)
        if usuario is None:
            return False
        self.usuarios.remove(usuario)
        return True