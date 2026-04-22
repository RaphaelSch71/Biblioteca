from services.biblioteca_service import BibliotecaService
from services.auth_service import AuthService
from models.usuario import Usuario
from models.bibliotecario import Bibliotecario
from ui.menu import Menu
import os
import sys
from pathlib import Path


def _carregar_env_local():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        chave, valor = line.split("=", 1)
        chave = chave.strip()
        valor = valor.strip().strip('"').strip("'")
        os.environ.setdefault(chave, valor)


def _as_bool(valor: str | None, default=False) -> bool:
    if valor is None:
        return default
    return valor.strip().lower() in {"1", "true", "yes", "on"}


def _garantir_admin_inicial(usuario_repo):
    # Só cria admin bootstrap se explicitamente habilitado por variável de ambiente.
    if os.getenv("BOOTSTRAP_ADMIN", "false").strip().lower() not in {"1", "true", "yes", "on"}:
        return

    if usuario_repo.listar():
        return

    nome_admin = os.getenv("ADMIN_NOME", "Administrador")
    matricula_admin = os.getenv("ADMIN_MATRICULA", "ADM001")
    senha_admin = os.getenv("ADMIN_SENHA", "admin")
    usuario_repo.salvar(Bibliotecario(nome_admin, matricula_admin, senha_admin))


def _iniciar_interface_grafica(biblioteca_service, auth_service):
    try:
        if sys.platform.startswith("win"):
            import ctypes
            myappid = "senac.bibliotecabd.app"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        from PySide6.QtGui import QIcon
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
        from ui.styles import APP_QSS
        from ui.login_window import LoginWindow
        from ui.main_window import MainWindow

        app = QApplication([])
        app.setStyle("Fusion")
        app.setStyleSheet(APP_QSS)

        project_root = Path(__file__).resolve().parent
        app_icon_path = project_root / "biblioteca.ico"
        if not app_icon_path.exists():
            app_icon_path = project_root / "biblioteca_icon.png"
        if not app_icon_path.exists():
            app_icon_path = project_root / "biblioteca.png"
        if not app_icon_path.exists():
            app_icon_path = project_root / "ui" / "assets" / "icons" / "app.svg"
        if app_icon_path.exists():
            app.setWindowIcon(QIcon(str(app_icon_path)))

        def abrir_login():
            login = LoginWindow(auth_service, on_login_success=abrir_main)
            login.show()
            QTimer.singleShot(0, login.showMaximized)
            app._login_window = login

        def abrir_main(usuario):
            janela = MainWindow(
                biblioteca_service,
                usuario,
                auth_service=auth_service,
                on_logout=abrir_login,
            )
            janela.show()
            QTimer.singleShot(0, janela.showMaximized)
            app._janela_principal = janela

        abrir_login()
        app.exec()
        return True
    except KeyboardInterrupt:
        print("Inicialização interrompida pelo usuário.")
        return False
    except Exception as e:
        print(f"Interface gráfica indisponível: {e}")
        return False

def main():
    _carregar_env_local()

    usando_memoria = False
    strict_sql = _as_bool(os.getenv("STRICT_SQL"), default=False)

    try:
        from repositories.sql.usuario_repository_sql import UsuarioRepositorySQL
        from repositories.sql.livro_repository_sql import LivroRepositorySQL
        from repositories.sql.emprestimo_repository_sql import EmprestimoRepositorySQL
        from repositories.sql.pedido_emprestimo_repository_sql import PedidoEmprestimoRepositorySQL

        usuario_repo = UsuarioRepositorySQL()
        livro_repo = LivroRepositorySQL()
        emprestimo_repo = EmprestimoRepositorySQL()
        pedido_repo = PedidoEmprestimoRepositorySQL()
        print("Modo de execução: SQL Server")
    except Exception as erro_sql:
        if strict_sql:
            raise RuntimeError(
                "STRICT_SQL está habilitado e a conexão SQL falhou. "
                "Verifique DB_SERVER/DB_NAME/DB_UID/DB_PWD/DB_TRUSTED e driver ODBC."
            ) from erro_sql

        print(f"Aviso: integração SQL indisponível ({erro_sql}). Usando memória.")
        from repositories.memory.usuario_repository_memoria import UsuarioRepositoryMemoria
        from repositories.memory.livro_repository_memoria import LivroRepositoryMemoria
        from repositories.memory.emprestimo_repository_memoria import EmprestimoRepositoryMemoria
        from repositories.memory.pedido_emprestimo_repository_memoria import PedidoEmprestimoRepositoryMemoria

        usuario_repo = UsuarioRepositoryMemoria()
        livro_repo = LivroRepositoryMemoria()
        emprestimo_repo = EmprestimoRepositoryMemoria()
        pedido_repo = PedidoEmprestimoRepositoryMemoria(livro_repo)
        usando_memoria = True
        print("Modo de execução: Memória (sem persistência no SQL Server)")

    if not usando_memoria:
        # Garante um usuário bibliotecário para primeiro acesso no modo SQL
        _garantir_admin_inicial(usuario_repo)

    # Services
    auth_service = AuthService(usuario_repo)
    biblioteca_service = BibliotecaService(
        livro_repo,
        usuario_repo,
        emprestimo_repo,
        pedido_repo,
    )

    if _iniciar_interface_grafica(biblioteca_service, auth_service):
        return

    try:
        # LOGIN
        matricula = input("Matrícula: ")
        senha = input("Senha: ")

        usuario_logado = auth_service.login(matricula, senha)

        # MENU
        menu = Menu(biblioteca_service, usuario_logado)
        menu.exibir()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()