from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from ui.styles import COLORS
from ui.widgets.mini_graph import MiniGraph

class SensorCard(QFrame):
    def __init__(self, title, unit, color="#00D4FF", show_graph=True):
        super().__init__()
        self.title = title
        self.color = color
        self._value = 0.0
        self.setObjectName("sensorCard")
        self.setStyleSheet(f"""
            QFrame#sensorCard {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_glow']};
                border-radius: 12px;
                border-top: 2px solid {color};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 10)
        layout.setSpacing(4)

        # Başlık
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font: 700 18px 'Segoe UI'; letter-spacing: 2px;")
        layout.addWidget(title_lbl)

        # Değer
        self.val_lbl = QLabel("—")
        self.val_lbl.setAlignment(Qt.AlignCenter)
        self.val_lbl.setStyleSheet(f"color: {color}; font: 700 36px 'Segoe UI';")
        layout.addWidget(self.val_lbl)

        # Birim
        unit_lbl = QLabel(unit)
        unit_lbl.setAlignment(Qt.AlignCenter)
        unit_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font: 700 14px 'Segoe UI';")
        layout.addWidget(unit_lbl)

        # Mini grafik
        if show_graph:
            self.graph = MiniGraph(color=color)
            layout.addWidget(self.graph)
        else:
            self.graph = None

    def update_value(self, v):
        self._value = v
        self.val_lbl.setText(str(v))
        if self.graph:
            if v == "—":
                self.graph.data.clear()
                self.graph.update()
            else:
                self.graph.add_value(float(v))
