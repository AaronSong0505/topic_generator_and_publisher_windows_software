from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit, QMessageBox, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal
import api_client

class LLMGenThread(QThread):
    result_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, topic, debug=False):
        super().__init__()
        self.topic = topic
        self.debug = debug

    def run(self):
        try:
            resp = api_client.generate_xhs_copy_and_prompt(self.topic, debug=self.debug)
            self.result_signal.emit(resp)
        except Exception as e:
            self.error_signal.emit(str(e))

class LLMGenWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.topic_label = QLabel('请输入发帖主题：')
        self.topic_input = QLineEdit()
        self.debug_checkbox = QCheckBox('调试模式（显示详细RPA流程日志）')
        self.gen_btn = QPushButton('生成文案与提示词')
        self.gen_btn.clicked.connect(self.on_generate)
        self.copy_label = QLabel('生成的小红书文案：')
        self.copy_text = QTextEdit()
        self.copy_text.setReadOnly(True)
        self.prompt_label = QLabel('生成的图片提示词：')
        self.prompt_text = QTextEdit()
        self.prompt_text.setReadOnly(True)
        layout.addWidget(self.topic_label)
        layout.addWidget(self.topic_input)
        layout.addWidget(self.debug_checkbox)
        layout.addWidget(self.gen_btn)
        layout.addWidget(self.copy_label)
        layout.addWidget(self.copy_text)
        layout.addWidget(self.prompt_label)
        layout.addWidget(self.prompt_text)
        self.setLayout(layout)

    def on_generate(self):
        topic = self.topic_input.text().strip()
        if not topic:
            QMessageBox.warning(self, '提示', '请输入发帖主题')
            return
        debug = self.debug_checkbox.isChecked()
        self.gen_btn.setEnabled(False)
        self.copy_text.setText('生成中...')
        self.prompt_text.setText('生成中...')
        self.thread = LLMGenThread(topic, debug=debug)
        self.thread.result_signal.connect(self.on_result)
        self.thread.error_signal.connect(self.on_error)
        self.thread.start()

    def on_result(self, resp):
        self.copy_text.setText(resp.get('copy', '无'))
        self.prompt_text.setText(resp.get('prompt', '无'))
        self.gen_btn.setEnabled(True)

    def on_error(self, msg):
        QMessageBox.critical(self, '错误', f'生成失败：{msg}')
        self.copy_text.setText('')
        self.prompt_text.setText('')
        self.gen_btn.setEnabled(True) 