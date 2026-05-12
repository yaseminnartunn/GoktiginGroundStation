from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from ui.styles import COLORS
from ui.widgets.side_menu import SideMenu
from ui.widgets.top_bar import TopBar
from ui.widgets.status_bar import StatusBar
from ui.pages.login_page import LoginPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.data_page import DataTablePage
from ui.pages.test_page import TestPage
from ui.pages.serial_settings_page import SerialSettingsPage

class MainWindow(QMainWindow):
    def __init__(self, state_bus, logo_path, colors):
        super().__init__()
        self.state_bus = state_bus
        self.setWindowTitle("GökTigin Ground Station — TEKNOFEST 2026")
        self.setMinimumSize(1280, 780)
        self.setStyleSheet(f"QMainWindow, QWidget {{ background: {COLORS['bg_primary']}; }}")

        self.logo_path = logo_path
        self.colors = colors

        # Central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Ana Stack (Login vs Dashboard)
        self.main_stack = QStackedWidget()
        main_layout.addWidget(self.main_stack)

        # Pages
        self.login_page = LoginPage(self.show_dashboard, self.logo_path, self.colors)
        
        # Build Dashboard Container
        self.dashboard_container = QWidget()
        self._build_dashboard_layout(self.dashboard_container)

        self.main_stack.addWidget(self.login_page)
        self.main_stack.addWidget(self.dashboard_container)
        self.main_stack.setCurrentWidget(self.login_page)

    def _build_dashboard_layout(self, container):
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sol menü
        self.side_menu = SideMenu(self.on_menu_click)
        layout.addWidget(self.side_menu)

        # Sağ taraf (TopBar, Stack, StatusBar)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top bar
        self.top_bar = TopBar(toggle_callback=self.toggle_menu)
        right_layout.addWidget(self.top_bar)

        # Content stack
        self.content_stack = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.data_page = DataTablePage()
        self.test_page = TestPage(self.state_bus)
        self.serial_page = SerialSettingsPage(
            self.state_bus,
            go_back_callback=lambda: self.on_menu_click("dashboard")
        )

        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.data_page)
        self.content_stack.addWidget(self.test_page)
        self.content_stack.addWidget(self.serial_page)

        right_layout.addWidget(self.content_stack, 1)

        # Status bar
        self.status_bar = StatusBar()
        right_layout.addWidget(self.status_bar)

        layout.addWidget(right_widget, 1)

    def toggle_menu(self):
        width = self.side_menu.width()
        new_width = 180 if width == 0 else 0
        
        self.menu_anim1 = QPropertyAnimation(self.side_menu, b"minimumWidth")
        self.menu_anim1.setDuration(300)
        self.menu_anim1.setStartValue(width)
        self.menu_anim1.setEndValue(new_width)
        self.menu_anim1.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.menu_anim2 = QPropertyAnimation(self.side_menu, b"maximumWidth")
        self.menu_anim2.setDuration(300)
        self.menu_anim2.setStartValue(width)
        self.menu_anim2.setEndValue(new_width)
        self.menu_anim2.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.menu_anim1.start()
        self.menu_anim2.start()

    def on_menu_click(self, key):
        self.side_menu.set_active(key)
        if key == "dashboard":
            self.content_stack.setCurrentIndex(0)
        elif key == "veriler":
            self.content_stack.setCurrentIndex(1)
        elif key == "test":
            self.content_stack.setCurrentIndex(2)
        elif key == "seri_ayar":
            self.content_stack.setCurrentIndex(3)

    def show_dashboard(self, success, username=None):
        if success:
            self.main_stack.setCurrentWidget(self.dashboard_container)
            # Controller can hook into this if needed
