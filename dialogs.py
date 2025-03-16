from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton

class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加任务")
        layout = QVBoxLayout()
        self.date_input = QLineEdit("YYYY-MM-DD")
        self.time_input = QLineEdit("HH:MM")
        self.desc_input = QLineEdit("任务描述")
        self.urgency_input = QLineEdit("0~10")
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self.accept)
        layout.addWidget(self.date_input)
        layout.addWidget(self.time_input)
        layout.addWidget(self.desc_input)
        layout.addWidget(self.urgency_input)
        layout.addWidget(self.add_btn)
        self.setLayout(layout)