from datetime import datetime, timedelta
import os
import secrets


class AuthService:
    _codigos_bibliotecario = {}

    def __init__(self, usuario_repository):
        self.usuario_repository = usuario_repository

    def login(self, matricula, senha):
        usuario = self.usuario_repository.buscar_por_matricula(matricula)

        if not usuario:
            raise Exception("Usuário não encontrado.")

        if usuario.senha != senha:
            raise Exception("Senha inválida.")

        return usuario

    def _limpar_codigos_expirados(self):
        agora = datetime.now()
        expirados = [c for c, exp in self._codigos_bibliotecario.items() if exp < agora]
        for c in expirados:
            self._codigos_bibliotecario.pop(c, None)

    def _tem_bibliotecario_cadastrado(self) -> bool:
        from models.bibliotecario import Bibliotecario

        usuarios = self.usuario_repository.listar()
        return any(isinstance(u, Bibliotecario) for u in usuarios)

    def gerar_codigo_bibliotecario(self, codigo_mestre):
        codigo_mestre = (codigo_mestre or "").strip()
        codigo_esperado = os.getenv("BIBLIOTECARIO_CODIGO_MASTER", "BIB-2101")
        if codigo_mestre != codigo_esperado:
            raise Exception("Código mestre inválido.")

        self._limpar_codigos_expirados()
        codigo = f"BIB-{secrets.token_hex(3).upper()}"
        self._codigos_bibliotecario[codigo] = datetime.now() + timedelta(minutes=10)
        return codigo

    def _validar_codigo_bibliotecario(self, codigo):
        self._limpar_codigos_expirados()
        codigo = (codigo or "").strip()
        expira_em = self._codigos_bibliotecario.get(codigo)
        if not expira_em:
            return False

        # Código de uso único
        self._codigos_bibliotecario.pop(codigo, None)
        return True

    def cadastrar(self, nome, matricula, senha, tipo="usuario", codigo_bibliotecario=None):
        from models.usuario import Usuario
        from models.bibliotecario import Bibliotecario

        nome = (nome or "").strip()
        matricula = (matricula or "").strip()
        senha = (senha or "").strip()
        tipo = (tipo or "usuario").strip().lower()

        if not nome or not matricula or not senha:
            raise Exception("Preencha nome, matrícula e senha.")

        if tipo not in {"usuario", "bibliotecario"}:
            raise Exception("Tipo de cadastro inválido.")

        existente = self.usuario_repository.buscar_por_matricula(matricula)
        if existente:
            msg = "Matrícula já cadastrada. Faça login com a conta existente ou use outra matrícula."
            if getattr(existente, "matricula", "") == "B001" and getattr(existente, "nome", "") == "Maria":
                msg += " Conta padrão detectada: matrícula B001 e senha admin."
            raise Exception(msg)

        if tipo == "bibliotecario":
            codigo_mestre = os.getenv("BIBLIOTECARIO_CODIGO_MASTER", "BIB-2026")
            codigo_informado = (codigo_bibliotecario or "").strip()

            if self._tem_bibliotecario_cadastrado():
                if not self._validar_codigo_bibliotecario(codigo_informado):
                    raise Exception("Código de bibliotecário inválido ou expirado.")
            else:
                # bootstrap: primeiro bibliotecário pode usar o código mestre
                if codigo_informado != codigo_mestre:
                    raise Exception("Para o primeiro bibliotecário, informe o código mestre.")

            usuario = Bibliotecario(nome, matricula, senha)
        else:
            usuario = Usuario(nome, matricula, senha)

        return self.usuario_repository.salvar(usuario)