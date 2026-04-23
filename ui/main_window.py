from __future__ import annotations

from pathlib import Path

try:
    from PySide6.QtCore import Qt, QDate, QDateTime, QSize, QTimer, QEasingCurve, QPropertyAnimation, QObject, QEvent, QVariantAnimation
    from PySide6.QtGui import QIcon, QColor
    from PySide6.QtWidgets import (
        QApplication,
        QAbstractItemView,
        QComboBox,
        QDateEdit,
        QFormLayout,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QInputDialog,
        QGraphicsDropShadowEffect,
        QGraphicsOpacityEffect,
        QProgressBar,
        QPushButton,
        QSpinBox,
        QStackedWidget,
        QStyle,
        QScrollArea,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    QMainWindow = object

from models.bibliotecario import Bibliotecario
from models.livro import Livro
from models.usuario import Usuario
from ui.styles import APP_QSS

ICON_DIR = Path(__file__).resolve().parent / "assets" / "icons"


if QMainWindow is not object:
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
                if obj.property("skipHoverEffect"):
                    return super().eventFilter(obj, event)
                if event.type() == QEvent.Enter and obj.objectName() == "SecondaryButton":
                    self._animar(obj, 16.0)
                elif event.type() == QEvent.Leave and obj.objectName() == "SecondaryButton":
                    self._animar(obj, 0.0)
            return super().eventFilter(obj, event)

    class MainWindow(QMainWindow):
        def __init__(self, biblioteca_service, usuario_logado, auth_service=None, on_logout=None):
            super().__init__()
            self.biblioteca_service = biblioteca_service
            self.usuario_logado = usuario_logado
            self.auth_service = auth_service
            self.on_logout = on_logout
            self._ultimo_codigo_biblio = ""
            self._mostrar_codigo_biblio = False
            self._pedidos_notificados = set()
            self._sidebar_visivel = True
            self._sidebar_compacto = False
            self._nav_buttons = []
            self._page_anim = None
            self._chart_mode = "livros"

            project_root = Path(__file__).resolve().parents[1]
            icon_path = project_root / "biblioteca.ico"
            if not icon_path.exists():
                icon_path = project_root / "biblioteca_icon.png"
            if not icon_path.exists():
                icon_path = project_root / "biblioteca.png"
            if not icon_path.exists():
                icon_path = ICON_DIR / "app.svg"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))

            self.setWindowTitle("BibliotecaBD | Painel Principal")
            self.setObjectName("MainWindow")
            self.resize(1360, 840)
            app_qss = QApplication.instance().styleSheet() if QApplication.instance() else ""
            self.setStyleSheet(app_qss or APP_QSS)

            root = QWidget()
            self.setCentralWidget(root)
            root_layout = QHBoxLayout(root)
            root_layout.setContentsMargins(18, 18, 18, 18)
            root_layout.setSpacing(18)

            self.sidebar = self._build_sidebar()
            self.topbar = self._build_topbar()
            self.stack = QStackedWidget()

            right = QWidget()
            right_layout = QVBoxLayout(right)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(12)
            right_layout.addWidget(self.topbar)
            right_layout.addWidget(self.stack, 1)

            root_layout.addWidget(self.sidebar)
            root_layout.addWidget(right, 1)

            self.page_dashboard = self._wrap_page_scroll(self._build_dashboard_page())
            self.page_livros = self._wrap_page_scroll(self._build_livros_page())
            self.page_usuarios = self._wrap_page_scroll(self._build_usuarios_page())
            self.page_emprestimos = self._wrap_page_scroll(self._build_emprestimos_page())
            self.page_relatorios = self._wrap_page_scroll(self._build_relatorios_page())

            self.stack.addWidget(self.page_dashboard)
            self.stack.addWidget(self.page_livros)
            if self._pode_gerenciar_usuarios():
                self.stack.addWidget(self.page_usuarios)
            if self._pode_gerenciar_emprestimos():
                self.stack.addWidget(self.page_emprestimos)
            self.stack.addWidget(self.page_relatorios)

            self._map_nav_buttons()
            self.show_dashboard()
            self.statusBar().showMessage("Sistema pronto.")
            self.refresh_all()

            self._secondary_hover_filter = SecondaryButtonHoverFilter(self)
            for botao in self.findChildren(QPushButton):
                botao.installEventFilter(self._secondary_hover_filter)

            self._timer_pedidos = QTimer(self)
            self._timer_pedidos.timeout.connect(self.refresh_pedidos_emprestimo)
            self._timer_pedidos.start(5000)

        # helpers
        def _set_icon(self, button: QPushButton, file_name: str, fallback):
            p = ICON_DIR / file_name
            button.setIcon(QIcon(str(p)) if p.exists() else self.style().standardIcon(fallback))
            button.setIconSize(QSize(16, 16))

        def _apply_shadow(self, widget: QWidget, blur=32, y=8, alpha=70):
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(blur)
            effect.setOffset(0, y)
            try:
                from PySide6.QtGui import QColor
                effect.setColor(QColor(10, 16, 32, alpha))
            except Exception:
                pass
            widget.setGraphicsEffect(effect)

        def _wrap_page_scroll(self, widget: QWidget):
            scroll = QScrollArea()
            scroll.setObjectName("PageScroll")
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QScrollArea.NoFrame)
            scroll.setWidget(widget)
            return scroll

        def _cell(self, table: QTableWidget, row: int, col: int, value):
            item = QTableWidgetItem("" if value is None else str(value))
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            table.setItem(row, col, item)

        def _ok(self, msg: str):
            self.statusBar().showMessage(msg, 4000)
            QMessageBox.information(self, "Sucesso", msg)

        def _err(self, msg: str):
            self.statusBar().showMessage(f"Erro: {msg}", 7000)
            QMessageBox.warning(self, "Erro", msg)

        def _confirm(self, title: str, msg: str) -> bool:
            r = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            return r == QMessageBox.Yes

        def _logout(self):
            try:
                if not self._confirm("Encerrar sessão", "Deseja sair da conta e voltar para o login?"):
                    return
                if hasattr(self, "_timer_pedidos") and self._timer_pedidos.isActive():
                    self._timer_pedidos.stop()
                if hasattr(self, "_timer") and self._timer.isActive():
                    self._timer.stop()

                callback_logout = self.on_logout if callable(self.on_logout) else None
                self.hide()
                self.close()
                if callback_logout is not None:
                    QTimer.singleShot(0, callback_logout)
            except Exception as e:
                self._err(str(e))

        def _pode_gerenciar_usuarios(self):
            from utils.permissoes import Permissao
            return hasattr(self.usuario_logado, "tem_permissao") and self.usuario_logado.tem_permissao(Permissao.GERENCIAR_USUARIOS)

        def _pode_gerenciar_emprestimos(self):
            from utils.permissoes import Permissao
            return hasattr(self.usuario_logado, "tem_permissao") and self.usuario_logado.tem_permissao(Permissao.GERENCIAR_EMPRESTIMOS)

        def _pode_gerenciar_livros(self):
            from utils.permissoes import Permissao
            return hasattr(self.usuario_logado, "tem_permissao") and self.usuario_logado.tem_permissao(Permissao.CADASTRAR_LIVRO)

        # shell
        def _nav_btn(self, text, icon_file, fallback):
            b = QPushButton(text)
            b.setObjectName("NavButton")
            b.setCursor(Qt.PointingHandCursor)
            b.setToolTip(text)
            b.setProperty("fullText", text)
            self._set_icon(b, icon_file, fallback)
            self._nav_buttons.append(b)
            return b

        def _build_sidebar(self):
            f = QFrame(); f.setObjectName("Sidebar"); f.setMinimumWidth(255); f.setMaximumWidth(255)
            lay = QVBoxLayout(f); lay.setContentsMargins(18, 18, 18, 18); lay.setSpacing(12)

            hero = QFrame(); hero.setObjectName("SidebarHero")
            hero_lay = QVBoxLayout(hero); hero_lay.setContentsMargins(16, 16, 16, 16); hero_lay.setSpacing(6)
            lbl_brand = QLabel("BibliotecaBD"); lbl_brand.setObjectName("SidebarTitle")
            lbl_tag = QLabel("Gestão moderna do acervo e dos empréstimos")
            lbl_tag.setWordWrap(True)
            lbl_tag.setObjectName("SidebarBody")
            perfil = "Bibliotecário" if isinstance(self.usuario_logado, Bibliotecario) else "Usuário"
            lbl_profile = QLabel(f"Perfil ativo: {perfil}")
            lbl_profile.setObjectName("SidebarChip")
            hero_lay.addWidget(lbl_brand)
            hero_lay.addWidget(lbl_tag)
            hero_lay.addWidget(lbl_profile)
            self.sidebar_hero = hero
            self._apply_shadow(hero, blur=24, y=6, alpha=60)

            user = QFrame(); user.setObjectName("SidebarUserCard")
            user_lay = QVBoxLayout(user); user_lay.setContentsMargins(16, 14, 16, 14); user_lay.setSpacing(4)
            user_nome = QLabel(self.usuario_logado.nome)
            user_nome.setObjectName("SidebarUserName")
            user_matricula = QLabel(self.usuario_logado.matricula)
            user_matricula.setObjectName("SidebarBody")
            user_lay.addWidget(user_nome)
            user_lay.addWidget(user_matricula)
            self.sidebar_user_card = user
            self._apply_shadow(user, blur=24, y=6, alpha=60)

            lay.addWidget(hero)
            lay.addWidget(user)
            lay.addSpacing(2)

            self.btn_dashboard = self._nav_btn("Dashboard", "dashboard.svg", QStyle.SP_DesktopIcon)
            self.btn_livros = self._nav_btn("Livros", "books.svg", QStyle.SP_FileDialogDetailedView)
            self.btn_usuarios = self._nav_btn("Usuários", "users.svg", QStyle.SP_DirHomeIcon)
            self.btn_emprestimos = self._nav_btn("Empréstimos", "loans.svg", QStyle.SP_BrowserReload)
            self.btn_relatorios = self._nav_btn("Relatórios", "report.svg", QStyle.SP_FileDialogInfoView)
            self.btn_sair = QPushButton("Sair"); self.btn_sair.setObjectName("DangerButton"); self._set_icon(self.btn_sair, "logout.svg", QStyle.SP_DialogCloseButton)

            self.btn_dashboard.clicked.connect(self.show_dashboard)
            self.btn_livros.clicked.connect(self.show_livros)
            self.btn_usuarios.clicked.connect(self.show_usuarios)
            self.btn_emprestimos.clicked.connect(self.show_emprestimos)
            self.btn_relatorios.clicked.connect(self.show_relatorios)
            self.btn_sair.clicked.connect(self._logout)

            for b in [self.btn_dashboard, self.btn_livros, self.btn_usuarios, self.btn_emprestimos, self.btn_relatorios]:
                lay.addWidget(b)
            lay.addStretch(1); lay.addWidget(self.btn_sair)
            self._apply_sidebar_mode()
            return f

        def _build_topbar(self):
            b = QFrame(); b.setObjectName("TopBar")
            lay = QHBoxLayout(b); lay.setContentsMargins(16, 10, 16, 10)
            t = QLabel("BibliotecaBD"); t.setObjectName("TopBarTitle")
            s = QLabel("Gestão de acervo e empréstimos"); s.setObjectName("TopBarSubtitle")
            self.lbl_clock = QLabel(""); self.lbl_clock.setObjectName("TopBarClock")
            perfil = "Bibliotecário" if isinstance(self.usuario_logado, Bibliotecario) else "Usuário"
            lbl_user = QLabel(f"Usuário: {self.usuario_logado.nome}")
            lbl_role = QLabel(f"Perfil: {perfil}")
            lbl_role.setObjectName("TopBarClock")
            self.lbl_live_status = QLabel("● Online")
            self.lbl_live_status.setObjectName("TopBarClock")
            self.btn_toggle_sidebar = QPushButton("Recolher menu")
            self.btn_toggle_sidebar.setObjectName("SecondaryButton")
            self.btn_toggle_sidebar.setProperty("skipHoverEffect", True)
            self.btn_toggle_sidebar.setFixedWidth(150)
            self._set_icon(self.btn_toggle_sidebar, "menu.svg", QStyle.SP_TitleBarMenuButton)
            self.btn_toggle_sidebar.clicked.connect(self._toggle_sidebar)
            lay.addWidget(t); lay.addWidget(s); lay.addWidget(self.btn_toggle_sidebar); lay.addStretch(1); lay.addWidget(self.lbl_live_status); lay.addWidget(lbl_user); lay.addWidget(lbl_role); lay.addWidget(self.lbl_clock)
            self._apply_shadow(b, blur=20, y=5, alpha=45)
            self._timer = QTimer(self); self._timer.timeout.connect(lambda: self.lbl_clock.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss"))); self._timer.start(1000)
            self.lbl_clock.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss"))
            return b

        def _page(self, title, subtitle):
            f = QFrame(); f.setObjectName("ContentCard")
            lay = QVBoxLayout(f); lay.setContentsMargins(22, 22, 22, 22); lay.setSpacing(14)
            h = QFrame(); h.setObjectName("Header")
            hl = QVBoxLayout(h); hl.setContentsMargins(20, 18, 20, 18)
            ttl = QLabel(title); ttl.setObjectName("PageTitle")
            sub = QLabel(subtitle); sub.setObjectName("PageSubtitle"); sub.setWordWrap(True)
            hl.addWidget(ttl); hl.addWidget(sub); lay.addWidget(h)
            return f, lay

        def _set_active(self, active: QPushButton):
            for b in [self.btn_dashboard, self.btn_livros, self.btn_usuarios, self.btn_emprestimos, self.btn_relatorios]:
                b.setProperty("active", b is active)
                b.style().unpolish(b); b.style().polish(b)

        def _apply_sidebar_mode(self):
            if not hasattr(self, "sidebar"):
                return

            if self._sidebar_compacto:
                self.sidebar.setMinimumWidth(84)
                self.sidebar.setMaximumWidth(84)
                for widget in [getattr(self, "sidebar_hero", None), getattr(self, "sidebar_user_card", None)]:
                    if widget is not None:
                        widget.hide()
                for b in self._nav_buttons:
                    b.setText("")
                    b.setProperty("compact", True)
                    b.style().unpolish(b); b.style().polish(b)
            else:
                self.sidebar.setMinimumWidth(255)
                self.sidebar.setMaximumWidth(255)
                for widget in [getattr(self, "sidebar_hero", None), getattr(self, "sidebar_user_card", None)]:
                    if widget is not None:
                        widget.show()
                for b in self._nav_buttons:
                    b.setText(b.property("fullText") or "")
                    b.setProperty("compact", False)
                    b.style().unpolish(b); b.style().polish(b)

        def _toggle_sidebar(self):
            self._sidebar_visivel = not self._sidebar_visivel
            self._sidebar_compacto = not self._sidebar_visivel
            self._apply_sidebar_mode()
            self.btn_toggle_sidebar.setText("Recolher menu" if self._sidebar_visivel else "Expandir menu")
            self.statusBar().showMessage(
                "Menu lateral compacto ativado." if self._sidebar_compacto else "Menu lateral expandido.",
                3000,
            )

        def _animate_page(self, target_widget: QWidget):
            if self.stack.currentWidget() is target_widget:
                return

            target_widget.setGraphicsEffect(None)
            effect = QGraphicsOpacityEffect(target_widget)
            effect.setOpacity(0.0)
            target_widget.setGraphicsEffect(effect)
            self.stack.setCurrentWidget(target_widget)

            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(220)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)

            def limpar():
                if target_widget.graphicsEffect() is effect:
                    target_widget.setGraphicsEffect(None)

            anim.finished.connect(limpar)
            self._page_anim = anim
            anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

        # dashboard
        def _metric_card(self, title, val, accent, icon, hint):
            c = QFrame(); c.setObjectName("DashboardCard")
            c.setStyleSheet(f"QFrame#DashboardCard{{border-left:5px solid {accent};}}")
            l = QVBoxLayout(c); l.setContentsMargins(18, 18, 18, 18)
            top = QHBoxLayout(); a = QLabel(title); a.setObjectName("MetricTitle"); i = QLabel(icon); i.setObjectName("MetricIcon")
            top.addWidget(a); top.addStretch(1); top.addWidget(i)
            v = QLabel(str(val)); v.setObjectName("MetricValue")
            h = QLabel(hint); h.setObjectName("MetricHint")
            l.addLayout(top); l.addWidget(v); l.addWidget(h)
            return c, v

        def _build_dashboard_page(self):
            p, lay = self._page("Dashboard", "Painel visual com os principais indicadores do sistema.")
            g = QGridLayout(); g.setHorizontalSpacing(12); g.setVerticalSpacing(12)
            c1, self.lbl_dash_books = self._metric_card("Total de livros", 0, "#4F7CFF", "📘", "Itens cadastrados")
            c2, self.lbl_dash_available = self._metric_card("Disponíveis", 0, "#22C55E", "✅", "Prontos para empréstimo")
            c3, self.lbl_dash_users = self._metric_card("Usuários", 0, "#14B8A6", "👤", "Leitores e bibliotecários")
            c4, self.lbl_dash_loans = self._metric_card("Empréstimos ativos", 0, "#F59E0B", "🔄", "Itens fora do acervo")
            g.addWidget(c1, 0, 0); g.addWidget(c2, 0, 1); g.addWidget(c3, 1, 0); g.addWidget(c4, 1, 1)
            for card in (c1, c2, c3, c4):
                self._apply_shadow(card)
            lay.addLayout(g)

            info_row = QHBoxLayout()
            info_row.setSpacing(12)

            about_card = QFrame(); about_card.setObjectName("InsightCard")
            about_layout = QVBoxLayout(about_card); about_layout.setContentsMargins(16, 16, 16, 16); about_layout.setSpacing(8)
            about_title = QLabel("Sobre o projeto"); about_title.setObjectName("InfoCardTitle")
            about_body = QLabel(
                "Aplicação em camadas (UI + Services + Repositories), integrada ao SQL Server "
                "com procedures, triggers e auditoria de eventos."
            )
            about_body.setObjectName("InfoCardBody"); about_body.setWordWrap(True)
            self.lbl_dash_last_refresh = QLabel("Última atualização: --")
            self.lbl_dash_last_refresh.setObjectName("InfoCardBody")
            about_layout.addWidget(about_title)
            about_layout.addWidget(about_body)
            about_layout.addWidget(self.lbl_dash_last_refresh)

            actions_card = QFrame(); actions_card.setObjectName("InsightCard")
            actions_layout = QVBoxLayout(actions_card); actions_layout.setContentsMargins(16, 16, 16, 16); actions_layout.setSpacing(8)
            actions_title = QLabel("Ações rápidas"); actions_title.setObjectName("InfoCardTitle")
            self.lbl_dash_health = QLabel("Status do acervo: --")
            self.lbl_dash_health.setObjectName("InfoCardBody")
            btn_go_livros = QPushButton("Ir para Livros"); btn_go_livros.setObjectName("SecondaryButton"); btn_go_livros.clicked.connect(self.show_livros)
            btn_go_relatorios = QPushButton("Ir para Relatórios"); btn_go_relatorios.setObjectName("SecondaryButton"); btn_go_relatorios.clicked.connect(self.show_relatorios)
            btn_refresh = QPushButton("Atualizar painel"); btn_refresh.setObjectName("PrimaryButton"); btn_refresh.clicked.connect(self.refresh_all)
            actions_layout.addWidget(actions_title)
            actions_layout.addWidget(self.lbl_dash_health)
            actions_layout.addWidget(btn_go_livros)
            actions_layout.addWidget(btn_go_relatorios)
            actions_layout.addWidget(btn_refresh)

            info_row.addWidget(about_card, 1)
            info_row.addWidget(actions_card, 1)
            lay.addLayout(info_row)

            self._apply_shadow(about_card, blur=26, y=8, alpha=55)
            self._apply_shadow(actions_card, blur=26, y=8, alpha=55)

            chart_card = QFrame(); chart_card.setObjectName("InsightCard")
            chart_layout = QVBoxLayout(chart_card); chart_layout.setContentsMargins(16, 16, 16, 16); chart_layout.setSpacing(10)
            chart_title = QLabel("📈 Painel dinâmico")
            chart_title.setObjectName("InfoCardTitle")
            chart_desc = QLabel("Clique em uma categoria para alternar a visualização do gráfico-resumo.")
            chart_desc.setObjectName("InfoCardBody")
            chart_desc.setWordWrap(True)

            chart_btns = QGridLayout()
            self.btn_chart_livros = QPushButton("Acervo")
            self.btn_chart_emprestimos = QPushButton("Empréstimos")
            self.btn_chart_usuarios = QPushButton("Usuários")
            for btn in (self.btn_chart_livros, self.btn_chart_emprestimos, self.btn_chart_usuarios):
                btn.setObjectName("SecondaryButton")
                btn.setMinimumHeight(34)
                btn.setMinimumWidth(120)

            chart_btns.setHorizontalSpacing(8)
            chart_btns.setVerticalSpacing(8)
            chart_btns.addWidget(self.btn_chart_livros, 0, 0)
            chart_btns.addWidget(self.btn_chart_emprestimos, 0, 1)
            chart_btns.addWidget(self.btn_chart_usuarios, 0, 2)

            self.chart_summary_title = QLabel("")
            self.chart_summary_title.setObjectName("InfoCardTitle")
            self.chart_summary_body = QLabel("")
            self.chart_summary_body.setObjectName("InfoCardBody")
            self.chart_summary_body.setWordWrap(True)

            self.chart_bar_a = QProgressBar(); self.chart_bar_b = QProgressBar(); self.chart_bar_c = QProgressBar()
            self.chart_bar_a.setFormat("%v")
            self.chart_bar_b.setFormat("%v")
            self.chart_bar_c.setFormat("%v")

            chart_layout.addWidget(chart_title)
            chart_layout.addWidget(chart_desc)
            chart_layout.addLayout(chart_btns)
            chart_layout.addWidget(self.chart_summary_title)
            chart_layout.addWidget(self.chart_summary_body)
            chart_layout.addWidget(self.chart_bar_a)
            chart_layout.addWidget(self.chart_bar_b)
            chart_layout.addWidget(self.chart_bar_c)
            self._apply_shadow(chart_card, blur=26, y=8, alpha=55)
            lay.addWidget(chart_card)

            self.btn_chart_livros.clicked.connect(lambda: self._set_dashboard_chart("livros"))
            self.btn_chart_emprestimos.clicked.connect(lambda: self._set_dashboard_chart("emprestimos"))
            self.btn_chart_usuarios.clicked.connect(lambda: self._set_dashboard_chart("usuarios"))
            self._set_dashboard_chart(self._chart_mode)
            return p

        def _set_dashboard_chart(self, mode: str):
            self._chart_mode = mode
            livros = self.biblioteca_service.listar_livros(self.usuario_logado)
            total_livros = len(livros)
            disponiveis = len([l for l in livros if l.disponivel])
            indisponiveis = max(0, total_livros - disponiveis)
            emps = self.biblioteca_service.listar_emprestimos(self.usuario_logado) if self._pode_gerenciar_emprestimos() else []
            ativos = len([e for e in emps if e.ativo])
            devolvidos = len([e for e in emps if not e.ativo])
            usuarios_total = self.biblioteca_service.usuario_repository.listar()
            users = len(usuarios_total)
            bibliotecarios = len([u for u in usuarios_total if isinstance(u, Bibliotecario)])
            leitores = max(0, users - bibliotecarios)

            if mode == "emprestimos":
                titulo = "Empréstimos"
                body = "Distribuição dos empréstimos ativos e devolvidos no sistema."
                valores = [("Ativos", ativos, "#F59E0B"), ("Devolvidos", devolvidos, "#22C55E"), ("Pendentes", max(0, total_livros - ativos - devolvidos), "#4F7CFF")]
            elif mode == "usuarios":
                titulo = "Usuários"
                body = "Volume de usuários e bibliotecários cadastrados."
                valores = [("Leitores", leitores, "#14B8A6"), ("Bibliotecários", bibliotecarios, "#A855F7"), ("Total", users, "#4F7CFF")]
            else:
                titulo = "Acervo"
                body = "Resumo visual da disponibilidade do acervo."
                valores = [("Disponíveis", disponiveis, "#22C55E"), ("Indisponíveis", indisponiveis, "#F59E0B"), ("Total", total_livros, "#4F7CFF")]

            self.chart_summary_title.setText(titulo)
            self.chart_summary_body.setText(body)

            bars = [self.chart_bar_a, self.chart_bar_b, self.chart_bar_c]
            max_value = max(1, max(valor for _, valor, _ in valores))
            for bar, (label, valor, cor) in zip(bars, valores):
                bar.setMaximum(max_value)
                bar.setValue(valor)
                bar.setFormat(f"{label}: {valor}")
                bar.setStyleSheet(f"QProgressBar::chunk{{background:{cor};}}")

            for bar in bars[len(valores):]:
                bar.setMaximum(1)
                bar.setValue(0)
                bar.setFormat("")

        # livros page
        def _build_livros_page(self):
            if self._pode_gerenciar_livros():
                p, lay = self._page("Livros", "Cadastro, atualização e exclusão de livros.")
                card = QFrame(); card.setObjectName("Header"); row = QHBoxLayout(card); row.setContentsMargins(16, 16, 16, 16)
                form = QFormLayout()
                self.livro_id = QLineEdit(); self.livro_id.setReadOnly(True)
                self.livro_titulo = QLineEdit(); self.livro_autor = QLineEdit(); self.livro_isbn = QLineEdit()
                self.livro_ano = QSpinBox(); self.livro_ano.setRange(0, 9999); self.livro_ano.setSpecialValueText("")
                for k, w in [("ID", self.livro_id), ("Título", self.livro_titulo), ("Autor", self.livro_autor), ("ISBN", self.livro_isbn), ("Ano", self.livro_ano)]:
                    form.addRow(k, w)
                btns = QVBoxLayout()
                for txt, obj, icon, cb in [
                    ("Novo", "PrimaryButton", "add.svg", self.salvar_livro),
                    ("Atualizar", "SecondaryButton", "edit.svg", self.atualizar_livro),
                    ("Excluir", "DangerButton", "delete.svg", self.excluir_livro),
                    ("Limpar", "SecondaryButton", "clear.svg", self.limpar_livro_form),
                ]:
                    b = QPushButton(txt); b.setObjectName(obj); self._set_icon(b, icon, QStyle.SP_CommandLink); b.clicked.connect(cb); btns.addWidget(b)
                btns.addStretch(1)
                row.addLayout(form, 2); row.addLayout(btns, 1)
                lay.addWidget(card)
            else:
                p, lay = self._page("Livros", "Visualização do acervo disponível.")

            self.tbl_livros = QTableWidget(0, 6)
            self.tbl_livros.setHorizontalHeaderLabels(["ID", "Título", "Autor", "ISBN", "Ano", "Disponível"])
            self.tbl_livros.setSelectionBehavior(QAbstractItemView.SelectRows); self.tbl_livros.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tbl_livros.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            if self._pode_gerenciar_livros():
                self.tbl_livros.itemSelectionChanged.connect(self.preencher_livro_form)
            lay.addWidget(self.tbl_livros, 1)
            return p

        # usuários page
        def _build_usuarios_page(self):
            p, lay = self._page("Usuários", "Cadastro e manutenção de usuários.")
            card = QFrame(); card.setObjectName("Header"); row = QHBoxLayout(card); row.setContentsMargins(16, 16, 16, 16)
            form = QFormLayout()
            self.usuario_id = QLineEdit(); self.usuario_id.setReadOnly(True)
            self.usuario_nome = QLineEdit(); self.usuario_matricula = QLineEdit(); self.usuario_senha = QLineEdit()
            self.usuario_tipo = QComboBox(); self.usuario_tipo.addItems(["usuario", "bibliotecario"])
            self.usuario_ativo = QComboBox(); self.usuario_ativo.addItems(["Sim", "Não"])
            for k, w in [("ID", self.usuario_id), ("Nome", self.usuario_nome), ("Matrícula", self.usuario_matricula), ("Senha", self.usuario_senha), ("Tipo", self.usuario_tipo), ("Ativo", self.usuario_ativo)]:
                form.addRow(k, w)
            btns = QVBoxLayout()
            for txt, obj, icon, cb in [
                ("Novo", "PrimaryButton", "add.svg", self.salvar_usuario),
                ("Atualizar", "SecondaryButton", "edit.svg", self.atualizar_usuario),
                ("Excluir", "DangerButton", "delete.svg", self.excluir_usuario),
                ("Limpar", "SecondaryButton", "clear.svg", self.limpar_usuario_form),
            ]:
                b = QPushButton(txt); b.setObjectName(obj); self._set_icon(b, icon, QStyle.SP_CommandLink); b.clicked.connect(cb); btns.addWidget(b)
            btns.addStretch(1)
            row.addLayout(form, 2); row.addLayout(btns, 1)

            self.tbl_usuarios = QTableWidget(0, 5)
            self.tbl_usuarios.setHorizontalHeaderLabels(["ID", "Nome", "Matrícula", "Tipo", "Ativo"])
            self.tbl_usuarios.setSelectionBehavior(QAbstractItemView.SelectRows); self.tbl_usuarios.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tbl_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.tbl_usuarios.itemSelectionChanged.connect(self.preencher_usuario_form)
            lay.addWidget(card); lay.addWidget(self.tbl_usuarios, 1)
            return p

        # empréstimos page
        def _build_emprestimos_page(self):
            p, lay = self._page("Empréstimos", "Controle de empréstimos e devoluções.")
            card = QFrame(); card.setObjectName("Header"); row = QHBoxLayout(card); row.setContentsMargins(16, 16, 16, 16)
            form = QFormLayout()
            self.emprestimo_id = QLineEdit(); self.emprestimo_id.setReadOnly(True)
            self.combo_livro = QComboBox(); self.combo_usuario = QComboBox()
            self.emprestimo_data = QDateEdit(); self.emprestimo_data.setCalendarPopup(True); self.emprestimo_data.setDate(QDate.currentDate())
            self.emprestimo_data_prevista = QDateEdit(); self.emprestimo_data_prevista.setCalendarPopup(True); self.emprestimo_data_prevista.setDate(QDate.currentDate().addDays(7))
            self.emprestimo_ativo = QComboBox(); self.emprestimo_ativo.addItems(["Sim", "Não"])
            for k, w in [("ID", self.emprestimo_id), ("Livro", self.combo_livro), ("Usuário", self.combo_usuario), ("Data", self.emprestimo_data), ("Prev. devolução", self.emprestimo_data_prevista), ("Ativo", self.emprestimo_ativo)]:
                form.addRow(k, w)
            btns = QVBoxLayout()
            for txt, obj, icon, cb in [
                ("Realizar", "PrimaryButton", "borrow.svg", self.salvar_emprestimo),
                ("Devolver", "SecondaryButton", "return.svg", self.devolver_emprestimo),
                ("Excluir", "DangerButton", "delete.svg", self.excluir_emprestimo),
                ("Limpar", "SecondaryButton", "clear.svg", self.limpar_emprestimo_form),
            ]:
                b = QPushButton(txt); b.setObjectName(obj); self._set_icon(b, icon, QStyle.SP_CommandLink); b.clicked.connect(cb); btns.addWidget(b)
            btns.addStretch(1)
            row.addLayout(form, 2); row.addLayout(btns, 1)

            self.tbl_emprestimos = QTableWidget(0, 9)
            self.tbl_emprestimos.setHorizontalHeaderLabels(["ID", "Livro", "ISBN", "Usuário", "Matrícula", "Empréstimo", "Prev. devolução", "Devolução", "Ativo"])
            self.tbl_emprestimos.setSelectionBehavior(QAbstractItemView.SelectRows); self.tbl_emprestimos.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tbl_emprestimos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.tbl_emprestimos.itemSelectionChanged.connect(self.preencher_emprestimo_form)
            lay.addWidget(card); lay.addWidget(self.tbl_emprestimos, 1)
            return p

        def _build_relatorios_page(self):
            p, lay = self._page("Relatórios", "Gráfico simples com indicadores-chave da biblioteca.")
            card = QFrame(); card.setObjectName("InsightCard")
            l = QVBoxLayout(card); l.setContentsMargins(18, 18, 18, 18); l.setSpacing(12)
            l.addWidget(QLabel("📊 Distribuição de Empréstimos"))
            self.bar_loans_active = QProgressBar(); self.bar_loans_active.setFormat("Ativos: %v")
            self.bar_loans_returned = QProgressBar(); self.bar_loans_returned.setFormat("Devolvidos: %v")
            self.bar_books_available = QProgressBar(); self.bar_books_available.setFormat("Livros disponíveis: %v")
            self.lbl_report_resume = QLabel(""); self.lbl_report_resume.setWordWrap(True); self.lbl_report_resume.setObjectName("InsightBody")
            for w in [self.bar_loans_active, self.bar_loans_returned, self.bar_books_available, self.lbl_report_resume]:
                l.addWidget(w)
            lay.addWidget(card); lay.addStretch(1)

            # Pedido de empréstimo pelo usuário comum
            if not isinstance(self.usuario_logado, Bibliotecario):
                card_loans = QFrame(); card_loans.setObjectName("InsightCard")
                ll = QVBoxLayout(card_loans); ll.setContentsMargins(18, 18, 18, 18); ll.setSpacing(10)
                ll.addWidget(QLabel("📚 Meus empréstimos"))

                self.tbl_meus_emprestimos = QTableWidget(0, 7)
                self.tbl_meus_emprestimos.setHorizontalHeaderLabels(["ID", "Livro", "Empréstimo", "Prev. devolução", "Devolução", "Ativo", "Status"])
                self.tbl_meus_emprestimos.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.tbl_meus_emprestimos.setEditTriggers(QAbstractItemView.NoEditTriggers)
                self.tbl_meus_emprestimos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                ll.addWidget(self.tbl_meus_emprestimos)
                lay.addWidget(card_loans)

                card_user = QFrame(); card_user.setObjectName("InsightCard")
                lu = QVBoxLayout(card_user); lu.setContentsMargins(18, 18, 18, 18); lu.setSpacing(10)
                lu.addWidget(QLabel("📨 Solicitar empréstimo"))

                self.combo_pedido_livro = QComboBox()
                self.combo_pedido_livro.setObjectName("LoginInput")

                self.btn_solicitar_pedido = QPushButton("Emitir pedido de empréstimo")
                self.btn_solicitar_pedido.setObjectName("PrimaryButton")
                self.btn_solicitar_pedido.clicked.connect(self.solicitar_pedido_emprestimo)

                self.tbl_meus_pedidos = QTableWidget(0, 6)
                self.tbl_meus_pedidos.setHorizontalHeaderLabels(["ID", "Livro", "Status", "Pedido", "Prev. Devolução", "Atendido por"])
                self.tbl_meus_pedidos.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.tbl_meus_pedidos.setEditTriggers(QAbstractItemView.NoEditTriggers)
                self.tbl_meus_pedidos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                self.lbl_notif_usuario = QLabel("Nenhuma notificação de empréstimo ativo.")
                self.lbl_notif_usuario.setObjectName("InsightBody")
                self.lbl_notif_usuario.setWordWrap(True)

                lu.addWidget(self.combo_pedido_livro)
                lu.addWidget(self.btn_solicitar_pedido)
                lu.addWidget(self.tbl_meus_pedidos)
                lu.addWidget(self.lbl_notif_usuario)
                lay.addWidget(card_user)

            # Fila de pedidos para bibliotecários
            if isinstance(self.usuario_logado, Bibliotecario):
                card_queue = QFrame(); card_queue.setObjectName("InsightCard")
                lq = QVBoxLayout(card_queue); lq.setContentsMargins(18, 18, 18, 18); lq.setSpacing(10)
                lq.addWidget(QLabel("🔔 Pedidos de empréstimo pendentes"))

                self.pedido_id = QLineEdit(); self.pedido_id.setReadOnly(True); self.pedido_id.setPlaceholderText("ID do pedido selecionado")
                self.pedido_data_prevista = QDateEdit(); self.pedido_data_prevista.setCalendarPopup(True); self.pedido_data_prevista.setDate(QDate.currentDate().addDays(7))
                self.btn_aceitar_pedido = QPushButton("Aceitar pedido e gerar empréstimo")
                self.btn_aceitar_pedido.setObjectName("PrimaryButton")
                self.btn_aceitar_pedido.clicked.connect(self.aceitar_pedido_emprestimo)

                self.tbl_pedidos_pendentes = QTableWidget(0, 6)
                self.tbl_pedidos_pendentes.setHorizontalHeaderLabels(["ID", "Livro", "ISBN", "Usuário", "Matrícula", "Data Pedido"])
                self.tbl_pedidos_pendentes.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.tbl_pedidos_pendentes.setEditTriggers(QAbstractItemView.NoEditTriggers)
                self.tbl_pedidos_pendentes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.tbl_pedidos_pendentes.itemSelectionChanged.connect(self.preencher_pedido_form)

                lq.addWidget(self.tbl_pedidos_pendentes)
                lq.addWidget(self.pedido_id)
                lq.addWidget(self.pedido_data_prevista)
                lq.addWidget(self.btn_aceitar_pedido)
                lay.addWidget(card_queue)

            if isinstance(self.usuario_logado, Bibliotecario):
                card_bib = QFrame(); card_bib.setObjectName("InsightCard")
                lb = QVBoxLayout(card_bib); lb.setContentsMargins(18, 18, 18, 18); lb.setSpacing(10)
                lb.addWidget(QLabel("🔐 Gerenciar códigos de bibliotecário"))

                self.btn_gerar_codigo_biblio = QPushButton("Gerar código para novo bibliotecário")
                self.btn_gerar_codigo_biblio.setObjectName("SecondaryButton")
                self.btn_gerar_codigo_biblio.clicked.connect(self.gerar_codigo_bibliotecario_painel)

                self.btn_copiar_codigo_biblio = QPushButton("Copiar último código")
                self.btn_copiar_codigo_biblio.setObjectName("PrimaryButton")
                self.btn_copiar_codigo_biblio.clicked.connect(self.copiar_codigo_bibliotecario_painel)

                self.btn_toggle_codigo_biblio = QPushButton("Revelar código")
                self.btn_toggle_codigo_biblio.setObjectName("SecondaryButton")
                self.btn_toggle_codigo_biblio.clicked.connect(self.toggle_codigo_bibliotecario_painel)

                self.lbl_codigo_biblio_gerado = QLabel("Nenhum código gerado nesta sessão.")
                self.lbl_codigo_biblio_gerado.setObjectName("InsightBody")
                self.lbl_codigo_biblio_gerado.setWordWrap(True)

                lb.addWidget(self.btn_gerar_codigo_biblio)
                lb.addWidget(self.btn_copiar_codigo_biblio)
                lb.addWidget(self.btn_toggle_codigo_biblio)
                lb.addWidget(self.lbl_codigo_biblio_gerado)
                lay.addWidget(card_bib)

            return p

        def gerar_codigo_bibliotecario_painel(self):
            try:
                if self.auth_service is None:
                    raise Exception("Serviço de autenticação indisponível.")

                codigo_mestre, ok = QInputDialog.getText(
                    self,
                    "Código mestre",
                    "Informe o código mestre para gerar novo código:",
                    QLineEdit.Password,
                )
                if not ok:
                    return

                codigo = self.auth_service.gerar_codigo_bibliotecario(codigo_mestre)
                self._ultimo_codigo_biblio = codigo
                self._mostrar_codigo_biblio = False
                self.btn_toggle_codigo_biblio.setText("Revelar código")
                self._atualizar_label_codigo_biblio()
                QMessageBox.information(self, "Código gerado", f"Novo código: {codigo}\nValidade: 10 minutos (uso único).")
            except Exception as e:
                self._err(str(e))

        def _atualizar_label_codigo_biblio(self):
            if not self._ultimo_codigo_biblio:
                self.lbl_codigo_biblio_gerado.setText("Nenhum código gerado nesta sessão.")
                return

            if self._mostrar_codigo_biblio:
                texto = self._ultimo_codigo_biblio
            else:
                texto = self._ultimo_codigo_biblio[:4] + "*" * max(0, len(self._ultimo_codigo_biblio) - 4)

            self.lbl_codigo_biblio_gerado.setText(f"Último código gerado: {texto} (uso único, 10 min)")

        def toggle_codigo_bibliotecario_painel(self):
            try:
                if not self._ultimo_codigo_biblio:
                    raise Exception("Nenhum código foi gerado ainda.")
                self._mostrar_codigo_biblio = not self._mostrar_codigo_biblio
                self.btn_toggle_codigo_biblio.setText("Ocultar código" if self._mostrar_codigo_biblio else "Revelar código")
                self._atualizar_label_codigo_biblio()
            except Exception as e:
                self._err(str(e))

        def copiar_codigo_bibliotecario_painel(self):
            try:
                if not self._ultimo_codigo_biblio:
                    raise Exception("Nenhum código foi gerado ainda.")
                QApplication.clipboard().setText(self._ultimo_codigo_biblio)
                self.statusBar().showMessage("Código copiado para a área de transferência.", 4000)
            except Exception as e:
                self._err(str(e))

        # pedidos de empréstimo
        def solicitar_pedido_emprestimo(self):
            try:
                livro = self.combo_pedido_livro.currentData()
                if livro is None:
                    raise ValueError("Selecione um livro disponível.")
                pedido_id = self.biblioteca_service.solicitar_pedido_emprestimo(self.usuario_logado, livro.id)
                self.refresh_pedidos_emprestimo()
                self._ok(f"Pedido #{pedido_id} emitido com sucesso.")
            except Exception as e:
                self._err(str(e))

        def preencher_pedido_form(self):
            if not hasattr(self, "tbl_pedidos_pendentes"):
                return
            r = self.tbl_pedidos_pendentes.currentRow()
            if r < 0:
                return
            self.pedido_id.setText(self.tbl_pedidos_pendentes.item(r, 0).text())

        def aceitar_pedido_emprestimo(self):
            try:
                if not self.pedido_id.text().strip():
                    raise ValueError("Selecione um pedido pendente.")
                self.biblioteca_service.aceitar_pedido_emprestimo(
                    self.usuario_logado,
                    int(self.pedido_id.text()),
                    self.pedido_data_prevista.date().toPython(),
                )
                self.pedido_id.clear()
                self.refresh_all()
                self._ok("Pedido aceito e empréstimo ativado.")
            except Exception as e:
                self._err(str(e))

        def refresh_pedidos_emprestimo(self):
            # Usuário comum: solicita e acompanha pedidos
            if hasattr(self, "combo_pedido_livro"):
                livros = [l for l in self.biblioteca_service.listar_livros(self.usuario_logado) if l.disponivel]
                self.combo_pedido_livro.clear()
                for l in livros:
                    self.combo_pedido_livro.addItem(f"{l.titulo} | {l.isbn}", l)

                pedidos = self.biblioteca_service.listar_meus_pedidos(self.usuario_logado)
                self.tbl_meus_pedidos.setRowCount(len(pedidos))
                for r, p in enumerate(pedidos):
                    atendido = p.get("bibliotecario_nome") or "-"
                    self._cell(self.tbl_meus_pedidos, r, 0, p.get("id"))
                    self._cell(self.tbl_meus_pedidos, r, 1, p.get("livro_titulo"))
                    self._cell(self.tbl_meus_pedidos, r, 2, p.get("status"))
                    self._cell(self.tbl_meus_pedidos, r, 3, p.get("data_pedido"))
                    self._cell(self.tbl_meus_pedidos, r, 4, p.get("data_prevista_devolucao"))
                    self._cell(self.tbl_meus_pedidos, r, 5, atendido)

                novos_aceitos = [p for p in pedidos if p.get("status") == "ACEITO" and p.get("id") not in self._pedidos_notificados]
                if novos_aceitos:
                    ultimo = novos_aceitos[0]
                    msg = (
                        f"Seu pedido #{ultimo.get('id')} foi aceito. "
                        f"Livro: {ultimo.get('livro_titulo')} | Prev. devolução: {ultimo.get('data_prevista_devolucao')}"
                    )
                    self.lbl_notif_usuario.setText(msg)
                    for p in novos_aceitos:
                        self._pedidos_notificados.add(p.get("id"))
                    QMessageBox.information(self, "Pedido aceito", msg)

            if hasattr(self, "tbl_meus_emprestimos"):
                emprestimos = self.biblioteca_service.listar_meus_emprestimos(self.usuario_logado)
                self.tbl_meus_emprestimos.setRowCount(len(emprestimos))
                for r, e in enumerate(emprestimos):
                    self._cell(self.tbl_meus_emprestimos, r, 0, e.id)
                    self._cell(self.tbl_meus_emprestimos, r, 1, e.livro.titulo)
                    self._cell(self.tbl_meus_emprestimos, r, 2, e.data_emprestimo)
                    self._cell(self.tbl_meus_emprestimos, r, 3, getattr(e, "data_prevista_devolucao", None))
                    self._cell(self.tbl_meus_emprestimos, r, 4, e.data_devolucao)
                    self._cell(self.tbl_meus_emprestimos, r, 5, "Sim" if e.ativo else "Não")
                    self._cell(self.tbl_meus_emprestimos, r, 6, "Em aberto" if e.ativo else "Encerrado")

            # Bibliotecário: fila pendente
            if hasattr(self, "tbl_pedidos_pendentes"):
                pendentes = self.biblioteca_service.listar_pedidos_pendentes(self.usuario_logado)
                self.tbl_pedidos_pendentes.setRowCount(len(pendentes))
                for r, p in enumerate(pendentes):
                    self._cell(self.tbl_pedidos_pendentes, r, 0, p.get("id"))
                    self._cell(self.tbl_pedidos_pendentes, r, 1, p.get("livro_titulo"))
                    self._cell(self.tbl_pedidos_pendentes, r, 2, p.get("livro_isbn"))
                    self._cell(self.tbl_pedidos_pendentes, r, 3, p.get("usuario_nome"))
                    self._cell(self.tbl_pedidos_pendentes, r, 4, p.get("usuario_matricula"))
                    self._cell(self.tbl_pedidos_pendentes, r, 5, p.get("data_pedido"))

        # forms + actions
        def limpar_livro_form(self):
            self.livro_id.clear(); self.livro_titulo.clear(); self.livro_autor.clear(); self.livro_isbn.clear(); self.livro_ano.setValue(0)

        def preencher_livro_form(self):
            if not hasattr(self, "livro_id"):
                return
            r = self.tbl_livros.currentRow()
            if r < 0: return
            self.livro_id.setText(self.tbl_livros.item(r, 0).text())
            self.livro_titulo.setText(self.tbl_livros.item(r, 1).text())
            self.livro_autor.setText(self.tbl_livros.item(r, 2).text())
            self.livro_isbn.setText(self.tbl_livros.item(r, 3).text())
            ano = self.tbl_livros.item(r, 4).text().strip(); self.livro_ano.setValue(int(ano) if ano.isdigit() else 0)

        def salvar_livro(self):
            try:
                self.biblioteca_service.cadastrar_livro(self.usuario_logado, Livro(None, self.livro_titulo.text().strip(), self.livro_autor.text().strip(), self.livro_isbn.text().strip(), None if self.livro_ano.value() == 0 else self.livro_ano.value()))
                self.refresh_all(); self.limpar_livro_form(); self._ok("Livro cadastrado com sucesso.")
            except Exception as e:
                self._err(str(e))

        def atualizar_livro(self):
            try:
                if not self.livro_id.text().strip(): raise ValueError("Selecione um livro na tabela.")
                self.biblioteca_service.atualizar_livro(self.usuario_logado, Livro(int(self.livro_id.text()), self.livro_titulo.text().strip(), self.livro_autor.text().strip(), self.livro_isbn.text().strip(), None if self.livro_ano.value() == 0 else self.livro_ano.value()))
                self.refresh_all(); self.limpar_livro_form(); self._ok("Livro atualizado com sucesso.")
            except Exception as e:
                self._err(str(e))

        def excluir_livro(self):
            try:
                if not self.livro_id.text().strip(): raise ValueError("Selecione um livro na tabela.")
                if not self._confirm("Confirmar exclusão", "Deseja realmente excluir este livro?"): return
                self.biblioteca_service.remover_livro(self.usuario_logado, int(self.livro_id.text()))
                self.refresh_all(); self.limpar_livro_form(); self._ok("Livro removido com sucesso.")
            except Exception as e:
                self._err(str(e))

        def limpar_usuario_form(self):
            self.usuario_id.clear(); self.usuario_nome.clear(); self.usuario_matricula.clear(); self.usuario_senha.clear(); self.usuario_tipo.setCurrentIndex(0); self.usuario_ativo.setCurrentIndex(0)

        def preencher_usuario_form(self):
            r = self.tbl_usuarios.currentRow()
            if r < 0: return
            self.usuario_id.setText(self.tbl_usuarios.item(r, 0).text())
            self.usuario_nome.setText(self.tbl_usuarios.item(r, 1).text())
            self.usuario_matricula.setText(self.tbl_usuarios.item(r, 2).text())
            self.usuario_tipo.setCurrentIndex(1 if self.tbl_usuarios.item(r, 3).text().strip().lower() == "bibliotecario" else 0)
            self.usuario_ativo.setCurrentIndex(0 if self.tbl_usuarios.item(r, 4).text().strip().lower() in {"sim", "true", "1"} else 1)

        def salvar_usuario(self):
            try:
                tipo = self.usuario_tipo.currentText()
                senha = self.usuario_senha.text().strip()
                if len(senha) < 1:
                    raise ValueError("Senha obrigatória: informe ao menos 1 caractere.")
                u = Bibliotecario(self.usuario_nome.text().strip(), self.usuario_matricula.text().strip(), senha) if tipo == "bibliotecario" else Usuario(self.usuario_nome.text().strip(), self.usuario_matricula.text().strip(), senha)
                u.ativo = self.usuario_ativo.currentText() == "Sim"
                self.biblioteca_service.cadastrar_usuario(self.usuario_logado, u)
                self.refresh_all(); self.limpar_usuario_form(); self._ok("Usuário cadastrado com sucesso.")
            except Exception as e:
                self._err(str(e))

        def atualizar_usuario(self):
            try:
                if not self.usuario_id.text().strip(): raise ValueError("Selecione um usuário na tabela.")
                tipo = self.usuario_tipo.currentText()
                senha_digitada = self.usuario_senha.text().strip()
                senha_para_salvar = ""
                senha_alterada = False
                if senha_digitada:
                    if not self._confirm("Confirmar alteração de senha", "Deseja realmente alterar a senha deste usuário?"):
                        senha_para_salvar = ""
                    else:
                        senha_para_salvar = senha_digitada
                        senha_alterada = True

                u = Bibliotecario(self.usuario_nome.text().strip(), self.usuario_matricula.text().strip(), senha_para_salvar) if tipo == "bibliotecario" else Usuario(self.usuario_nome.text().strip(), self.usuario_matricula.text().strip(), senha_para_salvar)
                u.id = int(self.usuario_id.text()); u.ativo = self.usuario_ativo.currentText() == "Sim"
                self.biblioteca_service.atualizar_usuario(self.usuario_logado, u)
                self.refresh_all(); self.limpar_usuario_form(); self._ok("Usuário atualizado com sucesso." if not senha_alterada else "Usuário e senha atualizados com sucesso.")
            except Exception as e:
                self._err(str(e))

        def excluir_usuario(self):
            try:
                if not self.usuario_id.text().strip(): raise ValueError("Selecione um usuário na tabela.")
                if not self._confirm("Confirmar exclusão", "Deseja realmente excluir este usuário?"): return
                self.biblioteca_service.remover_usuario(self.usuario_logado, int(self.usuario_id.text()))
                self.refresh_all(); self.limpar_usuario_form(); self._ok("Usuário removido com sucesso.")
            except Exception as e:
                self._err(str(e))

        def limpar_emprestimo_form(self):
            self.emprestimo_id.clear(); self.emprestimo_data.setDate(QDate.currentDate()); self.emprestimo_data_prevista.setDate(QDate.currentDate().addDays(7)); self.emprestimo_ativo.setCurrentIndex(0)
            if self.combo_livro.count(): self.combo_livro.setCurrentIndex(0)
            if self.combo_usuario.count(): self.combo_usuario.setCurrentIndex(0)

        def preencher_emprestimo_form(self):
            r = self.tbl_emprestimos.currentRow()
            if r < 0:
                return

            self.emprestimo_id.setText(self.tbl_emprestimos.item(r, 0).text())
            texto_data_prevista = self.tbl_emprestimos.item(r, 6).text().strip()
            data_prevista = QDate.fromString(texto_data_prevista, Qt.DateFormat.ISODate)
            if not data_prevista.isValid():
                data_prevista = QDate.currentDate().addDays(7)
            self.emprestimo_data_prevista.setDate(data_prevista)

        def salvar_emprestimo(self):
            try:
                l = self.combo_livro.currentData(); u = self.combo_usuario.currentData()
                if l is None or u is None: raise ValueError("Selecione livro e usuário.")
                self.biblioteca_service.realizar_emprestimo(
                    self.usuario_logado,
                    l,
                    u,
                    self.emprestimo_data_prevista.date().toPython(),
                )
                self.refresh_all(); self._ok("Empréstimo realizado com sucesso.")
            except Exception as e:
                self._err(str(e))

        def devolver_emprestimo(self):
            try:
                if not self.emprestimo_id.text().strip(): raise ValueError("Selecione um empréstimo na tabela.")
                emp = self.biblioteca_service.emprestimo_repository.buscar_por_id(int(self.emprestimo_id.text()))
                if emp is None: raise ValueError("Empréstimo não encontrado.")
                self.biblioteca_service.devolver_livro(self.usuario_logado, emp)
                self.refresh_all(); self._ok("Livro devolvido com sucesso.")
            except Exception as e:
                self._err(str(e))

        def excluir_emprestimo(self):
            try:
                if not self.emprestimo_id.text().strip(): raise ValueError("Selecione um empréstimo na tabela.")
                if not self._confirm("Confirmar exclusão", "Deseja realmente excluir este empréstimo?"): return
                self.biblioteca_service.remover_emprestimo(self.usuario_logado, int(self.emprestimo_id.text()))
                self.refresh_all(); self._ok("Empréstimo removido com sucesso.")
            except Exception as e:
                self._err(str(e))

        # refresh
        def refresh_dashboard(self):
            livros = self.biblioteca_service.listar_livros(self.usuario_logado)
            total_livros = len(livros); disp = len([l for l in livros if l.disponivel])
            users = len(self.biblioteca_service.usuario_repository.listar())
            if self._pode_gerenciar_emprestimos():
                loans = len([e for e in self.biblioteca_service.listar_emprestimos(self.usuario_logado) if e.ativo])
            else:
                loans = len([e for e in self.biblioteca_service.listar_meus_emprestimos(self.usuario_logado) if e.ativo])
            self.lbl_dash_books.setText(str(total_livros)); self.lbl_dash_available.setText(str(disp)); self.lbl_dash_users.setText(str(users)); self.lbl_dash_loans.setText(str(loans))

            disponibilidade = (disp / total_livros * 100) if total_livros else 0
            if hasattr(self, "lbl_dash_health"):
                if disponibilidade >= 70:
                    status = "saudável"
                elif disponibilidade >= 40:
                    status = "atenção"
                else:
                    status = "crítico"
                self.lbl_dash_health.setText(f"Status do acervo: {status} ({disponibilidade:.1f}% disponível)")

            if hasattr(self, "lbl_dash_last_refresh"):
                self.lbl_dash_last_refresh.setText(
                    f"Última atualização: {QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm:ss')}"
                )

            if hasattr(self, "lbl_live_status"):
                self.lbl_live_status.setText(f"● Atualizado {QDateTime.currentDateTime().toString('HH:mm:ss')}")

            if hasattr(self, "chart_summary_title"):
                self._set_dashboard_chart(self._chart_mode)

        def refresh_livros(self):
            livros = self.biblioteca_service.listar_livros(self.usuario_logado)
            self.tbl_livros.setRowCount(len(livros))
            for r, l in enumerate(livros):
                self._cell(self.tbl_livros, r, 0, l.id); self._cell(self.tbl_livros, r, 1, l.titulo); self._cell(self.tbl_livros, r, 2, l.autor)
                self._cell(self.tbl_livros, r, 3, l.isbn); self._cell(self.tbl_livros, r, 4, l.ano_publicacao); self._cell(self.tbl_livros, r, 5, "Sim" if l.disponivel else "Não")
            if hasattr(self, "combo_livro"):
                self.combo_livro.clear()
                for l in livros: self.combo_livro.addItem(f"{l.titulo} | {l.isbn}", l)

        def refresh_usuarios(self):
            if not self._pode_gerenciar_usuarios(): return
            users = self.biblioteca_service.listar_usuarios(self.usuario_logado)
            self.tbl_usuarios.setRowCount(len(users))
            for r, u in enumerate(users):
                self._cell(self.tbl_usuarios, r, 0, u.id); self._cell(self.tbl_usuarios, r, 1, u.nome); self._cell(self.tbl_usuarios, r, 2, u.matricula)
                self._cell(self.tbl_usuarios, r, 3, "bibliotecario" if isinstance(u, Bibliotecario) else "usuario")
                self._cell(self.tbl_usuarios, r, 4, "Sim" if getattr(u, "ativo", True) else "Não")
            if hasattr(self, "combo_usuario"):
                self.combo_usuario.clear()
                for u in users: self.combo_usuario.addItem(f"{u.nome} | {u.matricula}", u)

        def refresh_emprestimos(self):
            if not self._pode_gerenciar_emprestimos(): return
            emps = self.biblioteca_service.listar_emprestimos(self.usuario_logado)
            self.tbl_emprestimos.setRowCount(len(emps))
            for r, e in enumerate(emps):
                self._cell(self.tbl_emprestimos, r, 0, e.id); self._cell(self.tbl_emprestimos, r, 1, e.livro.titulo)
                self._cell(self.tbl_emprestimos, r, 2, e.livro.isbn); self._cell(self.tbl_emprestimos, r, 3, e.usuario.nome)
                self._cell(self.tbl_emprestimos, r, 4, e.usuario.matricula); self._cell(self.tbl_emprestimos, r, 5, e.data_emprestimo)
                self._cell(self.tbl_emprestimos, r, 6, getattr(e, "data_prevista_devolucao", None)); self._cell(self.tbl_emprestimos, r, 7, e.data_devolucao); self._cell(self.tbl_emprestimos, r, 8, "Sim" if e.ativo else "Não")

        def refresh_relatorios(self):
            livros = self.biblioteca_service.listar_livros(self.usuario_logado)
            total = len(livros); disp = len([l for l in livros if l.disponivel])
            emps = self.biblioteca_service.listar_emprestimos(self.usuario_logado) if self._pode_gerenciar_emprestimos() else []
            ativos = len([e for e in emps if e.ativo]); devolvidos = len([e for e in emps if not e.ativo])
            mx = max(1, ativos + devolvidos)
            self.bar_loans_active.setMaximum(mx); self.bar_loans_active.setValue(ativos)
            self.bar_loans_returned.setMaximum(mx); self.bar_loans_returned.setValue(devolvidos)
            self.bar_books_available.setMaximum(max(1, total)); self.bar_books_available.setValue(disp)
            pct = (disp / total * 100) if total else 0
            self.lbl_report_resume.setText(f"Acervo: {total} livro(s). Disponibilidade: {pct:.1f}%. Empréstimos ativos: {ativos}. Devolvidos: {devolvidos}.")

        def refresh_all(self):
            self.refresh_livros(); self.refresh_usuarios(); self.refresh_emprestimos(); self.refresh_dashboard(); self.refresh_relatorios(); self.refresh_pedidos_emprestimo()

        # nav
        def _map_nav_buttons(self):
            self._set_active(self.btn_dashboard)
            if not self._pode_gerenciar_usuarios(): self.btn_usuarios.hide()
            if not self._pode_gerenciar_emprestimos(): self.btn_emprestimos.hide()

        def show_dashboard(self):
            self._animate_page(self.page_dashboard); self._set_active(self.btn_dashboard)

        def show_livros(self):
            self._animate_page(self.page_livros); self._set_active(self.btn_livros)

        def show_usuarios(self):
            if self._pode_gerenciar_usuarios():
                self._animate_page(self.page_usuarios); self._set_active(self.btn_usuarios)

        def show_emprestimos(self):
            if self._pode_gerenciar_emprestimos():
                self._animate_page(self.page_emprestimos); self._set_active(self.btn_emprestimos)

        def show_relatorios(self):
            self._animate_page(self.page_relatorios); self._set_active(self.btn_relatorios)
else:
    class MainWindow:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("PySide6 não está instalado neste ambiente.")