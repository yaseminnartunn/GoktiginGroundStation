import math
import random

from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPen, QLinearGradient
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QLineEdit, QPushButton

class LoginPage(QWidget):
    # Basit kullanıcı veritabanı
    USERS = {
        "admin": "1234"
    }

    def __init__(self, on_login, logo_path, colors):
        super().__init__()
        self.on_login = on_login
        self.logo_path = logo_path
        self.colors = colors
        self._anim_phase = 0.0
        self._stars = []
        self._build_star_field()
        self._setup_ui()
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick_animation)
        self._anim_timer.start(33)

    def _build_star_field(self):
        rng = random.Random(2026)
        self._stars = []
        for _ in range(240):
            self._stars.append(
                (
                    rng.random(),          # x ratio
                    rng.random(),          # y ratio
                    rng.uniform(0.8, 2.2), # radius
                    rng.uniform(0, math.tau),  # phase
                    rng.randint(85, 220),  # base alpha
                )
            )

    def _tick_animation(self):
        self._anim_phase += 0.08
        self.update()

    def _setup_ui(self):
        self.setStyleSheet(
            f"""
            QWidget#loginRoot {{
                background: transparent;
            }}
            QFrame#loginCard {{
                background: rgba(8, 21, 41, 200);
                border: 1px solid rgba(0, 212, 255, 170);
                border-radius: 18px;
            }}
            QLabel#title {{
                color: {self.colors['text_primary']};
                font: 700 28px 'Segoe UI';
                letter-spacing: 2px;
            }}
            QLabel#subtitle {{
                color: {self.colors['text_secondary']};
                font: 600 13px 'Segoe UI';
                letter-spacing: 3px;
            }}
            QLabel#status {{
                color: {self.colors['accent_red']};
                font: 600 12px 'Segoe UI';
            }}
            QLineEdit {{
                background: rgba(4, 13, 28, 220);
                border: 1px solid rgba(43, 91, 140, 180);
                border-radius: 10px;
                color: {self.colors['text_primary']};
                font: 600 14px 'Segoe UI';
                padding: 12px 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {self.colors['accent_cyan']};
                background: rgba(6, 20, 42, 230);
            }}
            QPushButton {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00AEEA,
                    stop: 1 #00E5FF
                );
                color: #04121E;
                border: none;
                border-radius: 10px;
                font: 700 14px 'Segoe UI';
                letter-spacing: 2px;
                padding: 12px 14px;
            }}
            QPushButton:hover {{
                background: #7CF4FF;
            }}
        """
        )
        self.setObjectName("loginRoot")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        self.card = card
        card.setObjectName("loginCard")
        card.setFixedWidth(640)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 32, 40, 34)
        card_layout.setSpacing(14)

        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_pix = QPixmap(self.logo_path)
        if not logo_pix.isNull():
            logo_lbl.setPixmap(logo_pix.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        card_layout.addWidget(logo_lbl)

        title = QLabel("GÖKTİGİN HAVACILIK TAKIMLARI")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("DEEP SPACE GROUND CONTROL")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(8)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("KULLANICI ADI")
        card_layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("ŞİFRE")
        self.pass_input.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.pass_input)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("status")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.status_lbl)

        login_btn = QPushButton("SİSTEME BAĞLAN")
        login_btn.clicked.connect(self._try_login)
        card_layout.addWidget(login_btn)

        self.user_input.returnPressed.connect(self._try_login)
        self.pass_input.returnPressed.connect(self._try_login)

        root.addWidget(card)

    def _try_login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        
        if not username or not password:
            self.status_lbl.setText("Kullanıcı adı ve şifre zorunludur.")
            return
        
        # Kullanıcı doğrulama
        if username in self.USERS and self.USERS[username] == password:
            self.status_lbl.setText("")
            self.on_login(True, username)  # Başarılı giriş
        else:
            self.status_lbl.setText("Kullanıcı adı veya şifre hatalı.")
            self.pass_input.clear()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        # Tek renk (acik ton) uzay arkaplani
        p.fillRect(self.rect(), QColor("#032A47"))

        # Yıldız katmanı (deterministik dağılım)
        for x_ratio, y_ratio, radius, phase, base_alpha in self._stars:
            x = int(x_ratio * max(1, w - 1))
            y = int(y_ratio * max(1, h - 1))
            twinkle = 0.55 + 0.45 * ((math.sin(self._anim_phase + phase) + 1) / 2)
            alpha = int(base_alpha * twinkle)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(185, 225, 255, alpha))
            p.drawEllipse(x, y, int(radius), int(radius))

        # Login karti uzerinde scan-line efekti
        if hasattr(self, "card"):
            card_rect = self.card.geometry()
            if card_rect.height() > 24:
                travel = card_rect.height() - 24
                y_offset = int(((math.sin(self._anim_phase * 0.7) + 1) / 2) * travel)
                scan_rect = QRect(card_rect.left() + 8, card_rect.top() + y_offset, card_rect.width() - 16, 24)
                scan_grad = QLinearGradient(scan_rect.left(), scan_rect.top(), scan_rect.left(), scan_rect.bottom())
                scan_grad.setColorAt(0.0, QColor(0, 212, 255, 0))
                scan_grad.setColorAt(0.5, QColor(0, 212, 255, 65))
                scan_grad.setColorAt(1.0, QColor(0, 212, 255, 0))
                p.fillRect(scan_rect, scan_grad)
                p.setPen(QPen(QColor(0, 230, 255, 80), 1))
                p.drawLine(scan_rect.left(), scan_rect.center().y(), scan_rect.right(), scan_rect.center().y())
