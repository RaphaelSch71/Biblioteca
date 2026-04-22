try:
    from pathlib import Path
    from PySide6.QtGui import QIcon, QPixmap, QColor
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox,
        QFrame, QHBoxLayout, QGraphicsDropShadowEffect, QStackedWidget,
        QInputDialog, QScrollArea, QMessageBox, QApplication
    )
    from PySide6.QtCore import Qt, QVariantAnimation, QEasingCurve, QObject, QEvent
except ImportError:  # pragma: no cover - interface gráfica opcional
    QWidget = object
    QVBoxLayout = QLabel = QLineEdit = QPushButton = None

from services.auth_service import AuthService
from ui.styles import APP_QSS


LOGIN_LIGHT_OVERRIDE_QSS = """
QWidget#LoginWindow {
    background: #EAF2FF;
}

QWidget#LoginWindow QFrame#LoginCard,
QWidget#LoginWindow QFrame#LoginHero,
QWidget#LoginWindow QFrame#LoginInfoPanel,
QWidget#LoginWindow QFrame#LoginMediaCard {
    background: #FFFFFF;
    border: 1px solid #C7D6F7;
}

QWidget#LoginWindow QLabel {
    color: #102A56;
}

QWidget#LoginWindow QLineEdit,
QWidget#LoginWindow QComboBox {
    background: #F8FBFF;
    color: #102A56;
    border: 1px solid #AFC3EF;
}
"""


if QWidget is not object:
    class SecondaryButtonHoverFilter(QObject):
        def __init__(self, parent=None):
            super().__init__(parent)
            self._animacoes = {}

        def _animar(self, botao: QPushButton, destino: float):
            efeito = botao.graphicsEffect()
            if not isinstance(efeito, QGraphicsDropShadowEffect):
                efeito = QGraphicsDropShadowEffect(botao)
                efeito.setBlurRadius(0)
                efeito.setOffset(0, 0)
                efeito.setColor(QColor(79, 124, 255, 120))
                botao.setGraphicsEffect(efeito)

            anim = QVariantAnimation(botao)
            anim.setDuration(140)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.setStartValue(float(efeito.blurRadius()))
            anim.setEndValue(destino)

            def on_value(valor):
                r = float(valor)
                efeito.setBlurRadius(r)
                efeito.setOffset(0, 2.5 if r > 0 else 0)

            anim.valueChanged.connect(on_value)
            anim.finished.connect(lambda: self._animacoes.pop(id(botao), None))
            self._animacoes[id(botao)] = anim
            anim.start()

        def eventFilter(self, obj, event):
            if isinstance(obj, QPushButton):
                if event.type() == QEvent.Enter and obj.objectName() == "SecondaryButton":
                    self._animar(obj, 16.0)
                elif event.type() == QEvent.Leave and obj.objectName() == "SecondaryButton":
                    self._animar(obj, 0.0)
            return super().eventFilter(obj, event)

    class HoverPillLabel(QLabel):
        def __init__(self, texto: str, on_click=None):
            super().__init__(texto)
            self._c_base = QColor("#121F39")
            self._c_hover = QColor("#1D4ED8")
            self._c_border_base = QColor("#2A3B61")
            self._c_border_hover = QColor("#4F7CFF")
            self._progress = 0.0
            self._on_click = on_click

            self.setAlignment(Qt.AlignCenter)
            self.setCursor(Qt.PointingHandCursor)

            self._anim = QVariantAnimation(self)
            self._anim.setDuration(180)
            self._anim.setEasingCurve(QEasingCurve.OutCubic)
            self._anim.valueChanged.connect(self._on_anim_value)

            self._apply_style()

        def _mix(self, a: QColor, b: QColor, t: float) -> QColor:
            return QColor(
                int(a.red() + (b.red() - a.red()) * t),
                int(a.green() + (b.green() - a.green()) * t),
                int(a.blue() + (b.blue() - a.blue()) * t),
            )

        def _on_anim_value(self, value):
            self._progress = float(value)
            self._apply_style()

        def _apply_style(self):
            bg = self._mix(self._c_base, self._c_hover, self._progress)
            border = self._mix(self._c_border_base, self._c_border_hover, self._progress)
            self.setStyleSheet(
                f"background: {bg.name()};"
                f"border: 1px solid {border.name()};"
                "border-radius: 999px;"
                "padding: 6px 10px;"
                "color: #CFE0FF;"
                "font-size: 9.2pt;"
                "font-weight: 600;"
            )

        def enterEvent(self, event):
            self._anim.stop()
            self._anim.setStartValue(self._progress)
            self._anim.setEndValue(1.0)
            self._anim.start()
            super().enterEvent(event)

        def leaveEvent(self, event):
            self._anim.stop()
            self._anim.setStartValue(self._progress)
            self._anim.setEndValue(0.0)
            self._anim.start()
            super().leaveEvent(event)

        def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton and callable(self._on_click):
                self._on_click()
            super().mousePressEvent(event)

    class LoginWindow(QWidget):
        def __init__(self, auth_service: AuthService, on_login_success=None):
            super().__init__()
            self.setWindowTitle("BibliotecaBD | Acesso")
            self.resize(980, 560)
            self.setObjectName("LoginWindow")

            project_root = Path(__file__).resolve().parents[1]
            icon_path = project_root / "biblioteca.ico"
            if not icon_path.exists():
                icon_path = project_root / "biblioteca_icon.png"
            if not icon_path.exists():
                icon_path = project_root / "biblioteca.png"
            if not icon_path.exists():
                icon_path = Path(__file__).resolve().parent / "assets" / "icons" / "app.svg"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))

            self.auth_service = auth_service
            self.on_login_success = on_login_success
            self._tema_noturno_ativo = True

            root = QHBoxLayout(self)
            root.setContentsMargins(24, 24, 24, 24)
            root.setSpacing(0)
            self._root_layout = root

            self.left = QFrame()
            self.left.setObjectName("LoginHero")
            self.left.setMinimumWidth(320)
            left_layout = QVBoxLayout(self.left)
            left_layout.setContentsMargins(28, 28, 28, 28)
            left_layout.setSpacing(18)

            title = QLabel("BibliotecaBD")
            title.setObjectName("LoginTitle")
            subtitle = QLabel("Gestão elegante de livros, usuários e empréstimos em um fluxo simples, limpo e moderno.")
            subtitle.setWordWrap(True)
            subtitle.setObjectName("LoginSubtitle")

            highlight = QLabel("CRUD integrado\nProcedures, triggers e interface profissional")
            highlight.setObjectName("LoginHighlight")
            highlight.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            left_info = QFrame()
            left_info.setObjectName("LoginInfoPanel")
            left_info_layout = QVBoxLayout(left_info)
            left_info_layout.setContentsMargins(14, 12, 14, 12)
            left_info_layout.setSpacing(6)

            left_info_title = QLabel("Dicas rápidas")
            left_info_title.setObjectName("LoginInfoTitle")
            left_info_body = QLabel(
                "• Use sua matrícula institucional para entrar.\n"
                "• Cadastro de bibliotecário exige código válido.\n"
                "• Empréstimos e pedidos são atualizados em tempo real."
            )
            left_info_body.setObjectName("LoginInfoBody")
            left_info_body.setWordWrap(True)
            left_info_layout.addWidget(left_info_title)
            left_info_layout.addWidget(left_info_body)

            media_card = QFrame()
            media_card.setObjectName("LoginMediaCard")
            media_layout = QHBoxLayout(media_card)
            media_layout.setContentsMargins(12, 12, 12, 12)
            media_layout.setSpacing(10)

            media_image = QLabel("📚")
            media_image.setObjectName("LoginMediaImage")
            media_image.setAlignment(Qt.AlignCenter)
            media_image.setMinimumSize(64, 64)

            cover_path = project_root / "biblioteca.png"
            if cover_path.exists():
                pix = QPixmap(str(cover_path)).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                media_image.setPixmap(pix)

            media_text_col = QVBoxLayout()
            media_text_col.setSpacing(2)
            media_title = QLabel("Experiência moderna")
            media_title.setObjectName("LoginInfoTitle")
            media_body = QLabel("Painel dinâmico, controle de acesso e fluxo integrado de empréstimos.")
            media_body.setObjectName("LoginInfoBody")
            media_body.setWordWrap(True)
            media_text_col.addWidget(media_title)
            media_text_col.addWidget(media_body)

            media_layout.addWidget(media_image)
            media_layout.addLayout(media_text_col, 1)

            left_layout.addStretch(1)
            left_layout.addWidget(title)
            left_layout.addWidget(subtitle)
            left_layout.addWidget(highlight)
            left_layout.addWidget(left_info)
            left_layout.addWidget(media_card)
            left_layout.addStretch(1)

            card = QFrame()
            card.setObjectName("LoginCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(34, 34, 34, 34)
            card_layout.setSpacing(14)

            self.btn_tab_login = QPushButton("Entrar")
            self.btn_tab_login.setObjectName("PrimaryButton")
            self.btn_tab_cadastrar = QPushButton("Cadastrar")
            self.btn_tab_cadastrar.setObjectName("SecondaryButton")

            selector = QHBoxLayout()
            selector.setSpacing(8)
            selector.addWidget(self.btn_tab_login)
            selector.addWidget(self.btn_tab_cadastrar)

            self.forms_stack = QStackedWidget()

            # Página Entrar
            login_page = QFrame()
            login_layout = QVBoxLayout(login_page)
            login_layout.setContentsMargins(0, 0, 0, 0)
            login_layout.setSpacing(10)

            welcome = QLabel("Acesse o sistema")
            welcome.setObjectName("LoginCardTitle")
            welcome.setAlignment(Qt.AlignCenter)

            hint = QLabel("Use sua matrícula e senha para continuar.")
            hint.setObjectName("LoginCardHint")
            hint.setAlignment(Qt.AlignCenter)

            self.txt_usuario = QLineEdit()
            self.txt_usuario.setPlaceholderText("Matrícula")
            self.txt_usuario.setObjectName("LoginInput")

            self.txt_senha = QLineEdit()
            self.txt_senha.setPlaceholderText("Senha")
            self.txt_senha.setEchoMode(QLineEdit.Password)
            self.txt_senha.setObjectName("LoginInput")

            btn_login = QPushButton("Entrar")
            btn_login.setObjectName("PrimaryButton")
            btn_login.clicked.connect(self.login)

            login_layout.addWidget(welcome)
            login_layout.addWidget(hint)
            login_layout.addWidget(self.txt_usuario)
            login_layout.addWidget(self.txt_senha)
            login_layout.addWidget(btn_login)
            login_layout.addStretch(1)

            # Página Cadastrar
            register_page = QFrame()
            register_layout = QVBoxLayout(register_page)
            register_layout.setContentsMargins(0, 0, 0, 0)
            register_layout.setSpacing(10)

            register_title = QLabel("Crie sua conta")
            register_title.setObjectName("LoginCardTitle")
            register_title.setAlignment(Qt.AlignCenter)

            register_hint = QLabel("Informe os dados para cadastro no sistema.")
            register_hint.setObjectName("LoginCardHint")
            register_hint.setAlignment(Qt.AlignCenter)

            self.txt_cad_nome = QLineEdit()
            self.txt_cad_nome.setPlaceholderText("Nome completo")
            self.txt_cad_nome.setObjectName("LoginInput")

            self.txt_cad_matricula = QLineEdit()
            self.txt_cad_matricula.setPlaceholderText("Matrícula")
            self.txt_cad_matricula.setObjectName("LoginInput")

            self.txt_cad_senha = QLineEdit()
            self.txt_cad_senha.setPlaceholderText("Senha")
            self.txt_cad_senha.setEchoMode(QLineEdit.Password)
            self.txt_cad_senha.setObjectName("LoginInput")

            self.txt_cad_confirmar = QLineEdit()
            self.txt_cad_confirmar.setPlaceholderText("Confirmar senha")
            self.txt_cad_confirmar.setEchoMode(QLineEdit.Password)
            self.txt_cad_confirmar.setObjectName("LoginInput")

            self.cmb_cad_tipo = QComboBox()
            self.cmb_cad_tipo.setObjectName("LoginInput")
            self.cmb_cad_tipo.addItem("Usuário", "usuario")
            self.cmb_cad_tipo.addItem("Bibliotecário", "bibliotecario")
            self.cmb_cad_tipo.currentIndexChanged.connect(self._on_tipo_changed)

            self.txt_cad_codigo_biblio = QLineEdit()
            self.txt_cad_codigo_biblio.setPlaceholderText("Código de bibliotecário")
            self.txt_cad_codigo_biblio.setEchoMode(QLineEdit.Password)
            self.txt_cad_codigo_biblio.setObjectName("LoginInput")
            self.txt_cad_codigo_biblio.hide()

            self.btn_gerar_codigo_biblio = QPushButton("Gerar código randômico")
            self.btn_gerar_codigo_biblio.setObjectName("SecondaryButton")
            self.btn_gerar_codigo_biblio.clicked.connect(self.gerar_codigo_bibliotecario)
            self.btn_gerar_codigo_biblio.hide()

            btn_cadastrar = QPushButton("Cadastrar")
            btn_cadastrar.setObjectName("PrimaryButton")
            btn_cadastrar.clicked.connect(self.cadastrar)

            register_layout.addWidget(register_title)
            register_layout.addWidget(register_hint)
            register_layout.addWidget(self.txt_cad_nome)
            register_layout.addWidget(self.txt_cad_matricula)
            register_layout.addWidget(self.cmb_cad_tipo)
            register_layout.addWidget(self.txt_cad_codigo_biblio)
            register_layout.addWidget(self.btn_gerar_codigo_biblio)
            register_layout.addWidget(self.txt_cad_senha)
            register_layout.addWidget(self.txt_cad_confirmar)
            register_layout.addWidget(btn_cadastrar)
            register_layout.addStretch(1)

            self.forms_stack.addWidget(login_page)
            self.forms_stack.addWidget(register_page)

            self.status = QLabel("")
            self.status.setObjectName("LoginStatus")
            self.status.setAlignment(Qt.AlignCenter)

            forms_scroll = QScrollArea()
            forms_scroll.setObjectName("LoginScroll")
            forms_scroll.setWidgetResizable(True)
            forms_scroll.setFrameShape(QScrollArea.NoFrame)
            forms_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            forms_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            forms_scroll.setMinimumHeight(280)
            forms_scroll.setMaximumHeight(360)
            forms_scroll.setWidget(self.forms_stack)

            pill_row = QHBoxLayout()
            pill_row.setSpacing(8)

            pills = [
                ("🔒 Sessão segura", self._acao_sessao_segura),
                ("🎨 Tema noturno", self._acao_tema_noturno),
                ("🗄️ SQL Server", self._acao_sql_server),
            ]
            for texto, acao in pills:
                pill = HoverPillLabel(texto, on_click=acao)
                pill_row.addWidget(pill)

            card_layout.addSpacing(20)
            card_layout.addLayout(selector)
            card_layout.addSpacing(8)
            card_layout.addWidget(forms_scroll)
            card_layout.addWidget(self.status)
            card_layout.addLayout(pill_row)
            card_layout.addStretch(1)

            self.btn_tab_login.clicked.connect(self.show_login)
            self.btn_tab_cadastrar.clicked.connect(self.show_register)
            self.show_login()

            try:
                shadow = QGraphicsDropShadowEffect(self)
                shadow.setBlurRadius(28)
                shadow.setOffset(0, 10)
                card.setGraphicsEffect(shadow)
            except Exception:
                pass

            self.card_container = QFrame()
            card_container_layout = QVBoxLayout(self.card_container)
            card_container_layout.setContentsMargins(0, 0, 0, 0)
            card_container_layout.addWidget(card)

            root.addWidget(self.left, 1)
            root.addWidget(self.card_container, 1)

            self.setStyleSheet(APP_QSS)
            self.setMinimumSize(760, 520)

            self._secondary_hover_filter = SecondaryButtonHoverFilter(self)
            for botao in self.findChildren(QPushButton):
                botao.installEventFilter(self._secondary_hover_filter)

            self.txt_usuario.returnPressed.connect(self.login)
            self.txt_senha.returnPressed.connect(self.login)
            self.txt_cad_confirmar.returnPressed.connect(self.cadastrar)
            self._ajustar_layout_responsivo()

        def resizeEvent(self, event):
            super().resizeEvent(event)
            self._ajustar_layout_responsivo()

        def _ajustar_layout_responsivo(self):
            compacto = self.width() < 1040
            self.left.setVisible(not compacto)
            self._root_layout.setContentsMargins(14 if compacto else 24, 14 if compacto else 24, 14 if compacto else 24, 14 if compacto else 24)

        def show_login(self):
            self.forms_stack.setCurrentIndex(0)
            self.btn_tab_login.setObjectName("PrimaryButton")
            self.btn_tab_cadastrar.setObjectName("SecondaryButton")
            self.btn_tab_login.style().unpolish(self.btn_tab_login)
            self.btn_tab_login.style().polish(self.btn_tab_login)
            self.btn_tab_cadastrar.style().unpolish(self.btn_tab_cadastrar)
            self.btn_tab_cadastrar.style().polish(self.btn_tab_cadastrar)

        def show_register(self):
            self.forms_stack.setCurrentIndex(1)
            self.btn_tab_login.setObjectName("SecondaryButton")
            self.btn_tab_cadastrar.setObjectName("PrimaryButton")
            self.btn_tab_login.style().unpolish(self.btn_tab_login)
            self.btn_tab_login.style().polish(self.btn_tab_login)
            self.btn_tab_cadastrar.style().unpolish(self.btn_tab_cadastrar)
            self.btn_tab_cadastrar.style().polish(self.btn_tab_cadastrar)

        def _on_tipo_changed(self):
            tipo = self.cmb_cad_tipo.currentData()
            is_biblio = tipo == "bibliotecario"
            self.txt_cad_codigo_biblio.setVisible(is_biblio)
            self.btn_gerar_codigo_biblio.setVisible(is_biblio)

        def _acao_sessao_segura(self):
            QMessageBox.information(
                self,
                "Sessão segura",
                "Recursos ativos:\n"
                "• Autenticação por matrícula e senha\n"
                "• Validação de permissões por perfil\n"
                "• Regras de senha obrigatória no cadastro",
            )

        def _acao_tema_noturno(self):
            self._tema_noturno_ativo = not self._tema_noturno_ativo

            if self._tema_noturno_ativo:
                self.setStyleSheet(APP_QSS)
                self.status.setText("Tema noturno ativado.")
            else:
                self.setStyleSheet(APP_QSS + "\n" + LOGIN_LIGHT_OVERRIDE_QSS)
                self.status.setText("Tema claro ativado.")

        def _acao_sql_server(self):
            try:
                from database.connection import DatabaseConnection

                conn = DatabaseConnection.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT DB_NAME() AS DbName, @@SERVERNAME AS ServerName")
                row = cursor.fetchone()
                cursor.close()

                db_name = row[0] if row else "(desconhecido)"
                server_name = row[1] if row else "(desconhecido)"
                QMessageBox.information(
                    self,
                    "Status SQL Server",
                    f"Conexão ativa com SQL Server.\nServidor: {server_name}\nBanco: {db_name}",
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Status SQL Server",
                    f"Não foi possível validar a conexão SQL no momento.\nDetalhe: {e}",
                )

        def gerar_codigo_bibliotecario(self):
            try:
                codigo_mestre, ok = QInputDialog.getText(
                    self,
                    "Código mestre",
                    "Informe o código mestre para gerar código de bibliotecário:",
                    QLineEdit.Password,
                )
                if not ok:
                    return

                codigo = self.auth_service.gerar_codigo_bibliotecario(codigo_mestre)
                self.txt_cad_codigo_biblio.setText(codigo)
                self.status.setText("Código gerado. Validade: 10 minutos e uso único.")
            except Exception as e:
                self.status.setText(str(e))

        def login(self):
            try:
                usuario = self.auth_service.login(
                    self.txt_usuario.text(),
                    self.txt_senha.text()
                )
                self.status.setText(f"Bem-vindo, {usuario.nome}.")
                if callable(self.on_login_success):
                    self.on_login_success(usuario)
                self.close()
            except Exception as e:
                self.status.setText(str(e))

        def cadastrar(self):
            try:
                senha = self.txt_cad_senha.text()
                confirmar = self.txt_cad_confirmar.text()
                if senha != confirmar:
                    raise Exception("As senhas não conferem.")

                usuario = self.auth_service.cadastrar(
                    self.txt_cad_nome.text(),
                    self.txt_cad_matricula.text(),
                    senha,
                    tipo=self.cmb_cad_tipo.currentData(),
                    codigo_bibliotecario=self.txt_cad_codigo_biblio.text(),
                )

                self.status.setText(f"Cadastro realizado para {usuario.nome}. Faça login.")
                self.txt_usuario.setText(usuario.matricula)
                self.txt_senha.setText(senha)
                self.txt_cad_nome.clear()
                self.txt_cad_matricula.clear()
                self.txt_cad_senha.clear()
                self.txt_cad_confirmar.clear()
                self.txt_cad_codigo_biblio.clear()
                self.cmb_cad_tipo.setCurrentIndex(0)
                self.show_login()
            except Exception as e:
                self.status.setText(str(e))
else:
    class LoginWindow:
        def __init__(self, auth_service: AuthService, on_login_success=None):
            self.auth_service = auth_service
            self.on_login_success = on_login_success

        def show(self):
            raise RuntimeError("PySide6 não está instalado neste ambiente.")