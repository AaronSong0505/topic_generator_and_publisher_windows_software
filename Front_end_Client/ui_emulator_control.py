from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QTextEdit, QDialog, QDialogButtonBox
from PyQt5.QtCore import QTimer
import api_client

class ErrorDialog(QDialog):
    def __init__(self, error_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle('错误详情')
        self.resize(400, 200)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(error_text)
        layout.addWidget(self.text_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        self.setLayout(layout)

class EmulatorControlWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.refresh_status()
        # 定时刷新状态
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(3000)  # 每3秒刷新一次

    def init_ui(self):
        layout = QVBoxLayout()
        self.status_label = QLabel('模拟器状态: 未知')
        self.start_btn = QPushButton('启动模拟器')
        self.stop_btn = QPushButton('关闭模拟器')
        self.start_btn.clicked.connect(self.start_emulator)
        self.stop_btn.clicked.connect(self.stop_emulator)
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        self.setLayout(layout)

    def refresh_status(self):
        try:
            status = api_client.get_emulator_status()
            self.status_label.setText(f"模拟器状态: {status.get('status', '未知')}")
        except Exception as e:
            self.status_label.setText('模拟器状态: 获取失败')

    def start_emulator(self):
        try:
            resp = api_client.start_emulator()
            QMessageBox.information(self, '提示', resp.get('msg', '已发送启动指令'))
            self.refresh_status()
        except Exception as e:
            self.show_error_dialog(str(e))

    def stop_emulator(self):
        try:
            resp = api_client.stop_emulator()
            QMessageBox.information(self, '提示', resp.get('msg', '已发送关闭指令'))
            self.refresh_status()
        except Exception as e:
            self.show_error_dialog(str(e))

    def show_error_dialog(self, error_text):
        dlg = ErrorDialog(error_text, self)
        dlg.exec_() 