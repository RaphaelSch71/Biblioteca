APP_QSS = """
QWidget {
    font-family: 'Segoe UI';
    font-size: 10.5pt;
    color: #EAF0FF;
    background: #0F172A;
}

QWidget#LoginWindow, QWidget#MainWindow {
    background: #0B1120;
}

QMainWindow {
    background: #0B1120;
}

QFrame#LoginHero, QFrame#Sidebar, QFrame#Header, QFrame#ContentCard, QFrame#LoginCard {
    background: #111A2E;
    border: 1px solid #24324F;
    border-radius: 18px;
}

QFrame#SidebarHero, QFrame#SidebarUserCard {
    background: #0F1B32;
    border: 1px solid #24324F;
    border-radius: 16px;
}

QFrame#TopBar {
    background: #111A2E;
    border: 1px solid #24324F;
    border-radius: 14px;
}

QLabel#TopBarTitle {
    font-size: 14pt;
    font-weight: 700;
    color: #F8FBFF;
}

QLabel#TopBarSubtitle {
    color: #AFC0F5;
    font-size: 10pt;
}

QLabel#TopBarClock {
    color: #D6E2FF;
    font-weight: 600;
    background: #16233E;
    border: 1px solid #2C3E63;
    border-radius: 10px;
    padding: 6px 10px;
}

QScrollArea#PageScroll {
    background: transparent;
    border: none;
}

QScrollArea#PageScroll > QWidget > QWidget {
    background: transparent;
}

QLabel#SidebarTitle {
    font-size: 18pt;
    font-weight: 800;
    color: #FFFFFF;
}

QLabel#SidebarBody {
    color: #AFC0F5;
    font-size: 9.8pt;
}

QLabel#SidebarChip {
    background: #1D4ED8;
    color: white;
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 9pt;
    font-weight: 700;
    max-width: 160px;
}

QLabel#SidebarUserName {
    font-size: 12pt;
    font-weight: 700;
    color: #F8FBFF;
}

QFrame#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0F172A, stop:1 #111C35);
}

QFrame#LoginCard {
    background: #111A2E;
}

QFrame#LoginInfoPanel, QFrame#LoginMiniCard {
    background: #0F1B32;
    border: 1px solid #2A3B61;
    border-radius: 12px;
}

QFrame#LoginMediaCard {
    background: #0F1B32;
    border: 1px solid #2A3B61;
    border-radius: 12px;
}

QLabel#LoginMediaImage {
    background: #1D4ED8;
    border: 1px solid #4F7CFF;
    border-radius: 10px;
    padding: 4px;
    font-size: 20pt;
}

QLabel#LoginPill {
    background: #121F39;
    border: 1px solid #2A3B61;
    border-radius: 999px;
    padding: 6px 10px;
    color: #CFE0FF;
    font-size: 9.2pt;
    font-weight: 600;
}

QLabel#LoginInfoTitle {
    color: #EAF0FF;
    font-size: 10pt;
    font-weight: 700;
}

QLabel#LoginInfoBody {
    color: #AFC0F5;
    font-size: 9.4pt;
}

QScrollArea#LoginScroll {
    background: transparent;
    border: none;
}

QScrollArea#LoginScroll > QWidget > QWidget {
    background: transparent;
}

QFrame#DashboardCard {
    background: #111A2E;
    border: 1px solid #24324F;
    border-radius: 16px;
}

QLabel#MetricTitle {
    color: #BFD0FF;
    font-size: 9.5pt;
    font-weight: 600;
    text-transform: uppercase;
}

QLabel#MetricValue {
    color: #FFFFFF;
    font-size: 26pt;
    font-weight: 700;
}

QLabel#MetricIcon {
    font-size: 18pt;
}

QLabel#MetricHint {
    color: #93A4D4;
    font-size: 9pt;
}

QFrame#InsightCard {
    background: #0F1B32;
    border: 1px solid #2A3B61;
    border-radius: 14px;
}

QLabel#InsightTitle {
    color: #DCE7FF;
    font-size: 11.5pt;
    font-weight: 700;
}

QLabel#InsightBody {
    color: #AFC0F5;
    font-size: 10pt;
}

QLabel#InfoCardTitle {
    color: #EAF0FF;
    font-size: 11pt;
    font-weight: 700;
}

QLabel#InfoCardBody {
    color: #B9C8EE;
    font-size: 9.8pt;
}

QLabel#LoginTitle {
    font-size: 28pt;
    font-weight: 700;
    color: #FFFFFF;
}

QLabel#LoginSubtitle {
    font-size: 11pt;
    color: #C8D3F5;
    line-height: 1.4;
}

QLabel#LoginHighlight {
    background: #1D4ED8;
    border-radius: 14px;
    padding: 18px;
    color: white;
    font-size: 11pt;
    font-weight: 600;
}

QLabel#LoginCardTitle {
    font-size: 20pt;
    font-weight: 700;
    color: #FFFFFF;
}

QLabel#LoginCardHint, QLabel#LoginStatus {
    color: #98A2C3;
}

QLineEdit, QComboBox, QDateEdit, QSpinBox {
    background: #0B1223;
    border: 1px solid #2A3552;
    border-radius: 12px;
    padding: 10px 12px;
    color: #F4F7FF;
    selection-background-color: #4F7CFF;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
    border: 1px solid #4F7CFF;
}

QLineEdit[readOnly="true"] {
    color: #93A4D4;
    background: #0A1020;
}

QComboBox::drop-down, QDateEdit::drop-down, QSpinBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    background: #0B1223;
    border: 1px solid #2A3552;
    selection-background-color: #274B8E;
}

QSpinBox::up-button, QSpinBox::down-button {
    width: 18px;
    border: none;
    background: #15213A;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: #223155;
}

QPushButton {
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 600;
}

QPushButton#PrimaryButton {
    background: #4F7CFF;
    color: white;
}

QPushButton#PrimaryButton:hover {
    background: #6B8EFF;
}

QPushButton#PrimaryButton:pressed,
QPushButton#SecondaryButton:pressed,
QPushButton#DangerButton:pressed,
QPushButton#NavButton:pressed {
    padding-top: 11px;
    padding-bottom: 9px;
}

QPushButton#SecondaryButton {
    background: #22375D;
    color: #F3F7FF;
    border: 1px solid #3E5F97;
}

QPushButton#SecondaryButton:hover {
    background: #2E4776;
}

QPushButton#DangerButton {
    background: #E44F5A;
    color: white;
}

QPushButton#DangerButton:hover {
    background: #F0646E;
}

QPushButton#NavButton {
    background: #111F39;
    color: #EEF4FF;
    text-align: left;
    padding: 12px 16px;
    border-radius: 12px;
    border: 1px solid #223A62;
    font-weight: 700;
}

QPushButton#NavButton[compact="true"] {
    text-align: center;
    padding: 12px 10px;
}

QPushButton#NavButton:hover {
    background: #1E3054;
}

QPushButton#NavButton[compact="true"]:hover {
    background: #27406C;
}

QPushButton#NavButton[active="true"] {
    background: #223B6D;
    color: white;
}

QTableWidget {
    background: #0B1223;
    alternate-background-color: #111B31;
    border: 1px solid #24324F;
    border-radius: 14px;
    gridline-color: #26324A;
    selection-background-color: #274B8E;
    selection-color: white;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #1C2740;
}

QTableWidget::item:selected {
    background: #274B8E;
    color: white;
}

QHeaderView::section {
    background: #15213A;
    color: #D8E2FF;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #24324F;
    font-weight: 600;
}

QTabWidget::pane {
    border: none;
}

QScrollArea {
    border: none;
    background: transparent;
}

QStatusBar {
    background: #0B1120;
    color: #AFC0F5;
}

QMessageBox {
    background: #111A2E;
}

QToolTip {
    background: #111A2E;
    color: #EAF0FF;
    border: 1px solid #24324F;
}
"""


LIGHT_QSS = """
QWidget {
    font-family: 'Segoe UI';
    font-size: 11pt;
    color: #0C2A54;
    background: #E3ECFF;
}

QWidget#LoginWindow, QWidget#MainWindow, QMainWindow {
    background: #E3ECFF;
}

QFrame#LoginHero, QFrame#Sidebar, QFrame#Header, QFrame#ContentCard, QFrame#LoginCard,
QFrame#TopBar, QFrame#DashboardCard, QFrame#InsightCard, QFrame#LoginInfoPanel,
QFrame#LoginMiniCard, QFrame#LoginMediaCard, QFrame#SidebarHero, QFrame#SidebarUserCard {
    background: #F8FBFF;
    border: 1px solid #B4C7EC;
    border-radius: 16px;
}

QFrame#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #F7FBFF, stop:1 #E7F0FF);
}

QLabel#TopBarTitle, QLabel#SidebarTitle, QLabel#LoginTitle, QLabel#LoginCardTitle {
    color: #0A2F66;
    font-weight: 800;
}

QLabel#TopBarSubtitle, QLabel#SidebarBody, QLabel#InfoCardBody,
QLabel#LoginSubtitle, QLabel#LoginInfoBody, QLabel#InsightBody,
QLabel#MetricHint, QLabel#LoginCardHint, QLabel#LoginStatus {
    color: #1F4A82;
    font-weight: 600;
}

QLabel#TopBarClock {
    color: #0B3569;
    background: #E3EEFF;
    border: 1px solid #9FB9E8;
    border-radius: 10px;
    padding: 6px 10px;
    font-weight: 700;
}

QLabel#SidebarChip {
    background: #2F63D9;
    color: #FFFFFF;
    border-radius: 999px;
    padding: 6px 10px;
    font-weight: 700;
}

QLabel#SidebarUserName, QLabel#InfoCardTitle, QLabel#InsightTitle, QLabel#MetricTitle {
    color: #0D3A73;
    font-weight: 700;
}

QLabel#MetricValue {
    color: #0C2F5F;
    font-size: 26pt;
    font-weight: 800;
}

QLabel#LoginHighlight {
    background: #376CE1;
    color: #FFFFFF;
    border-radius: 14px;
    padding: 18px;
    font-weight: 700;
}

QLabel#LoginMediaImage {
    background: #DDE9FF;
    border: 1px solid #87AAE8;
    border-radius: 10px;
    padding: 4px;
}

QLineEdit, QComboBox, QDateEdit, QSpinBox {
    background: #FFFFFF;
    border: 2px solid #A6BEEA;
    border-radius: 12px;
    padding: 10px 12px;
    color: #0F2A52;
    selection-background-color: #3B6EE3;
    selection-color: #FFFFFF;
}

QLineEdit::placeholder {
    color: #4B6795;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
    border: 2px solid #2F63D9;
    background: #F8FBFF;
}

QLineEdit[readOnly="true"] {
    color: #496B9B;
    background: #F4F8FF;
}

QComboBox QAbstractItemView {
    background: #FFFFFF;
    color: #0F2A52;
    border: 1px solid #AFC5EE;
    selection-background-color: #DCE8FF;
    selection-color: #0F2A52;
}

QPushButton {
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
    min-height: 38px;
}

QPushButton#PrimaryButton {
    background: #3F73E8;
    color: #FFFFFF;
}

QPushButton#PrimaryButton:hover {
    background: #2F63D9;
}

QPushButton#SecondaryButton {
    background: #E5EEFF;
    color: #103D75;
    border: 1px solid #9FB8E8;
}

QPushButton#SecondaryButton:hover {
    background: #D8E6FF;
}

QPushButton#DangerButton {
    background: #E55353;
    color: #FFFFFF;
}

QPushButton#DangerButton:hover {
    background: #CD4242;
}

QPushButton#NavButton {
    background: transparent;
    color: #11396F;
    text-align: left;
    padding: 12px 16px;
    border-radius: 12px;
    font-weight: 700;
}

QPushButton#NavButton:hover {
    background: #DDE8FF;
}

QPushButton#NavButton[active="true"] {
    background: #C7DBFF;
    color: #0B3569;
    border: 1px solid #8FAEE5;
}

QTableWidget {
    background: #FFFFFF;
    alternate-background-color: #EEF4FF;
    border: 1px solid #AFC4EB;
    border-radius: 14px;
    gridline-color: #C7D7F2;
    selection-background-color: #3F73E8;
    selection-color: #FFFFFF;
    color: #143D73;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #DCE8FA;
}

QTableWidget::item:selected {
    background: #3F73E8;
    color: #FFFFFF;
}

QHeaderView::section {
    background: #E3EEFF;
    color: #0D3A73;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #AFC4EB;
    font-weight: 800;
    font-size: 10.5pt;
}

QProgressBar {
    background: #E8F0FF;
    color: #0D3A73;
    border: 1px solid #AFC4EB;
    border-radius: 8px;
    text-align: center;
    font-weight: 700;
}

QProgressBar::chunk {
    background: #4F7CFF;
    border-radius: 7px;
}

QScrollArea#PageScroll, QScrollArea#LoginScroll, QScrollArea {
    background: transparent;
    border: none;
}

QStatusBar {
    background: #E3ECFF;
    color: #1A467D;
    font-weight: 600;
}

QMessageBox {
    background: #FFFFFF;
    color: #0F2A52;
}

QToolTip {
    background: #FFFFFF;
    color: #0F2A52;
    border: 1px solid #AFC4EB;
}

QScrollBar:vertical {
    background: #E2ECFF;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #90AEE5;
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar:horizontal {
    background: #E2ECFF;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #90AEE5;
    border-radius: 5px;
    min-width: 24px;
}

QLabel#PageTitle {
    color: #0A2F66;
    font-size: 20pt;
    font-weight: 800;
}

QLabel#PageSubtitle {
    color: #1F4A82;
    font-size: 10.5pt;
    font-weight: 600;
}
"""