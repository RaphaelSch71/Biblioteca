from models.emprestimo import Emprestimo
from utils.permissoes import Permissao
from exceptions.permissoes_exception import PermissaoNegadaError

class BibliotecaService:
    def __init__(self, livro_repo, usuario_repo, emprestimo_repo, pedido_repo=None):
        self.livro_repository = livro_repo
        self.usuario_repository = usuario_repo
        self.emprestimo_repository = emprestimo_repo
        self.pedido_emprestimo_repository = pedido_repo

    @staticmethod
    def _is_erro_isbn_duplicado(erro: Exception) -> bool:
        msg = str(erro).lower()
        return (
            "isbn já cadastrado" in msg
            or "isbn ja cadastrado" in msg
            or "50020" in msg
            or "50210" in msg
            or "isbn já cadastrado para outro livro" in msg
            or "isbn ja cadastrado para outro livro" in msg
        )

    def cadastrar_livro(self, funcionario, livro):
        if not funcionario.tem_permissao(Permissao.CADASTRAR_LIVRO):
            raise PermissaoNegadaError()

        try:
            if hasattr(self.livro_repository, "salvar"):
                self.livro_repository.salvar(livro)
            else:
                self.livro_repository.cadastrar_livro(livro)
        except Exception as e:
            if self._is_erro_isbn_duplicado(e):
                raise Exception("Impossível cadastrar novo livro, dados já existentes.")
            raise

        return livro


    def listar_livros(self, usuario):
        if not usuario.tem_permissao(Permissao.LISTAR_LIVROS):
            raise PermissaoNegadaError()

        return self.livro_repository.listar()
    
    def realizar_emprestimo(self, funcionario, livro, usuario, data_prevista_devolucao=None):
        if not funcionario.tem_permissao(Permissao.REALIZAR_EMPRESTIMO):
            raise PermissaoNegadaError()

        if hasattr(self.emprestimo_repository, "realizar_emprestimo"):
            return self.emprestimo_repository.realizar_emprestimo(livro, usuario, data_prevista_devolucao)

        emprestimo = Emprestimo(livro, usuario)
        emprestimo.data_prevista_devolucao = data_prevista_devolucao
        emprestimo.realizar()
        self.emprestimo_repository.salvar(emprestimo)
        return emprestimo

    def devolver_livro(self, funcionario, emprestimo):
        if not funcionario.tem_permissao(Permissao.DEVOLVER_LIVRO):
            raise PermissaoNegadaError()

        if hasattr(self.emprestimo_repository, "devolver_emprestimo"):
            return self.emprestimo_repository.devolver_emprestimo(emprestimo)

        emprestimo.devolver()
        return emprestimo

    # ------------------------------
    # CRUD de usuários
    # ------------------------------
    def cadastrar_usuario(self, funcionario, usuario):
        if not funcionario.tem_permissao(Permissao.GERENCIAR_USUARIOS):
            raise PermissaoNegadaError()
        senha = (getattr(usuario, "senha", "") or "").strip()
        if len(senha) < 1:
            raise Exception("Senha obrigatória: informe ao menos 1 caractere.")
        usuario.senha = senha
        return self.usuario_repository.salvar(usuario)

    def listar_usuarios(self, funcionario):
        if not funcionario.tem_permissao(Permissao.GERENCIAR_USUARIOS):
            raise PermissaoNegadaError()
        return self.usuario_repository.listar()

    def atualizar_usuario(self, funcionario, usuario):
        if not funcionario.tem_permissao(Permissao.GERENCIAR_USUARIOS):
            raise PermissaoNegadaError()

        existente = self.usuario_repository.buscar_por_id(getattr(usuario, "id", None))
        if existente is None:
            raise Exception("Usuário não encontrado para atualização.")

        senha_informada = (getattr(usuario, "senha", "") or "").strip()
        if len(senha_informada) >= 1:
            usuario.senha = senha_informada
        else:
            # Sem nova senha informada: mantém senha atual do cadastro.
            existente_com_senha = self.usuario_repository.buscar_por_matricula(existente.matricula)
            senha_atual = (getattr(existente_com_senha, "senha", "") or "").strip() if existente_com_senha else ""
            if len(senha_atual) < 1:
                raise Exception("Senha obrigatória: não é permitido salvar usuário sem senha.")
            usuario.senha = senha_atual

        return self.usuario_repository.atualizar(usuario)

    def remover_usuario(self, funcionario, usuario_id):
        if not funcionario.tem_permissao(Permissao.GERENCIAR_USUARIOS):
            raise PermissaoNegadaError()
        return self.usuario_repository.remover(usuario_id)

    # ------------------------------
    # CRUD de livros
    # ------------------------------
    def atualizar_livro(self, funcionario, livro):
        if not funcionario.tem_permissao(Permissao.CADASTRAR_LIVRO):
            raise PermissaoNegadaError()

        try:
            return self.livro_repository.atualizar(livro)
        except Exception as e:
            if self._is_erro_isbn_duplicado(e):
                raise Exception("Impossível atualizar livro, dados já existentes.")
            raise

    def remover_livro(self, funcionario, livro_id):
        if not funcionario.tem_permissao(Permissao.REMOVER_LIVRO):
            raise PermissaoNegadaError()
        return self.livro_repository.remover(livro_id)

    # ------------------------------
    # CRUD de empréstimos
    # ------------------------------
    def listar_emprestimos(self, funcionario):
        if not funcionario.tem_permissao(Permissao.REALIZAR_EMPRESTIMO):
            raise PermissaoNegadaError()
        return self.emprestimo_repository.listar()

    def listar_meus_emprestimos(self, usuario):
        if not usuario.tem_permissao(Permissao.LISTAR_LIVROS):
            raise PermissaoNegadaError()

        if hasattr(self.emprestimo_repository, "listar_por_usuario"):
            return self.emprestimo_repository.listar_por_usuario(usuario.id)

        emprestimos = self.emprestimo_repository.listar()
        return [e for e in emprestimos if getattr(e.usuario, "id", None) == getattr(usuario, "id", None)]

    def atualizar_emprestimo(self, funcionario, emprestimo):
        if not funcionario.tem_permissao(Permissao.GERENCIAR_EMPRESTIMOS):
            raise PermissaoNegadaError()
        return self.emprestimo_repository.atualizar(emprestimo)

    def remover_emprestimo(self, funcionario, emprestimo_id):
        if not funcionario.tem_permissao(Permissao.GERENCIAR_EMPRESTIMOS):
            raise PermissaoNegadaError()
        return self.emprestimo_repository.remover(emprestimo_id)

    # ------------------------------
    # Pedidos de empréstimo
    # ------------------------------
    def solicitar_pedido_emprestimo(self, usuario, livro_id):
        if not usuario.tem_permissao(Permissao.LISTAR_LIVROS):
            raise PermissaoNegadaError()
        if self.pedido_emprestimo_repository is None:
            raise Exception("Módulo de pedidos de empréstimo indisponível.")
        return self.pedido_emprestimo_repository.solicitar(usuario.id, livro_id)

    def listar_pedidos_pendentes(self, funcionario):
        if not funcionario.tem_permissao(Permissao.GERENCIAR_EMPRESTIMOS):
            raise PermissaoNegadaError()
        if self.pedido_emprestimo_repository is None:
            return []
        pedidos = self.pedido_emprestimo_repository.listar_pendentes()
        for p in pedidos:
            if not p.get("livro_titulo"):
                livro = self.livro_repository.buscar_por_id(p.get("livro_id"))
                if livro is not None:
                    p["livro_titulo"] = livro.titulo
                    p["livro_isbn"] = livro.isbn
            if not p.get("usuario_nome"):
                usr = self.usuario_repository.buscar_por_id(p.get("usuario_id"))
                if usr is not None:
                    p["usuario_nome"] = usr.nome
                    p["usuario_matricula"] = usr.matricula
        return pedidos

    def listar_meus_pedidos(self, usuario):
        if not usuario.tem_permissao(Permissao.LISTAR_LIVROS):
            raise PermissaoNegadaError()
        if self.pedido_emprestimo_repository is None:
            return []
        pedidos = self.pedido_emprestimo_repository.listar_por_usuario(usuario.id)
        for p in pedidos:
            if not p.get("livro_titulo"):
                livro = self.livro_repository.buscar_por_id(p.get("livro_id"))
                if livro is not None:
                    p["livro_titulo"] = livro.titulo
                    p["livro_isbn"] = livro.isbn
        return pedidos

    def aceitar_pedido_emprestimo(self, funcionario, pedido_id, data_prevista_devolucao):
        if not funcionario.tem_permissao(Permissao.GERENCIAR_EMPRESTIMOS):
            raise PermissaoNegadaError()
        if self.pedido_emprestimo_repository is None:
            raise Exception("Módulo de pedidos de empréstimo indisponível.")
        return self.pedido_emprestimo_repository.aceitar(
            pedido_id,
            funcionario.id,
            data_prevista_devolucao,
        )
