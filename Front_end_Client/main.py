import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QListWidget, QWidget, QHBoxLayout, QListWidgetItem
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap, QIcon, QPainter, QColor
from PyQt5.QtCore import Qt
from ui_emulator_control import EmulatorControlWidget
from ui_llm_copy_prompt import LLMGenWidget
import os

def get_chinese_style_qss():
    return """
    QWidget {
        background-color: transparent;
        font-family: "FZKai-Z03S", "楷体", "STKaiti", "SimKai", serif;
        font-size: 16px;
        color: #3e2c1a;
    }
    QMainWindow {
        background-color: transparent;
    }
    QListWidget {
        background: rgba(237,227,210,0.85);
        border: none;
        font-size: 18px;
        color: #5b4636;
    }
    QListWidget::item:selected {
        background: #c7b299;
        color: #fff;
    }
    QPushButton {
        background-color: #ede3d2;
        border: 1px solid #c7b299;
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 17px;
        color: #5b4636;
    }
    QPushButton:hover {
        background-color: #d6c3a1;
    }
    QLabel {
        font-size: 18px;
        color: #3e2c1a;
        background: transparent;
    }
    QDialog {
        background-color: #f8f5f0;
    }
    QTextEdit {
        background: #fffbe8;
        border: 1px solid #c7b299;
        font-size: 15px;
        color: #3e2c1a;
    }
    """

class BgWidget(QWidget):
    def __init__(self, bg_path, parent=None):
        super().__init__(parent)
        self.bg_path = bg_path
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        # 先画米色底色
        painter.fillRect(self.rect(), QColor(248, 245, 240))  # 米色
        if os.path.exists(self.bg_path):
            pixmap = QPixmap(self.bg_path)
            # 保持比例铺满整个窗口
            scaled = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('全自动小红书文案生成与发布 - 前端')
        self.resize(900, 650)
        self.init_ui()

    def init_ui(self):
        # 使用自定义背景控件
        bg_path = os.path.join(os.path.dirname(__file__), 'assets', 'bg_ink.png')
        self.bg_widget = BgWidget(bg_path)
        layout = QHBoxLayout(self.bg_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.nav_list = QListWidget()
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon_emulator.png')
        if os.path.exists(icon_path):
            self.nav_list.addItem(QListWidgetItem(QIcon(icon_path), '模拟器控制'))
        else:
            self.nav_list.addItem('模拟器控制')
        self.nav_list.addItem('文案生成')
        self.stack = QStackedWidget()
        self.emulator_control = EmulatorControlWidget()
        self.stack.addWidget(self.emulator_control)
        self.llm_gen_widget = LLMGenWidget()
        self.stack.addWidget(self.llm_gen_widget)
        self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        layout.addWidget(self.nav_list, 1)
        layout.addWidget(self.stack, 4)
        self.setCentralWidget(self.bg_widget)
        self.nav_list.setCurrentRow(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 设置全局字体（优先楷体）
    app.setFont(QFont("FZKai-Z03S", 16))
    # 设置古风QSS
    app.setStyleSheet(get_chinese_style_qss())
    win = MainWindow()
    win.show()
    sys.exit(app.exec_()) 