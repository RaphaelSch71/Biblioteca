from models.usuario import Usuario

class UsuarioService:
    def __init__(self, usuario_repository=None):
        self.usuarios = []
        self.repo = usuario_repository
        self.proximo_id = 1

    def cadastrar_usuario(self, nome, matricula, senha):
        usuario = Usuario(nome, matricula, senha)

        if self.repo is not None:
            self.repo.salvar(usuario)
        else:
            self.usuarios.append(usuario)

        self.proximo_id += 1
        return usuario

    def listar_usuarios(self):
        if self.repo is not None:
            return self.repo.listar()

        return list(self.usuarios)