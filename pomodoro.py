from PyQt5.QtCore import QObject, QTimer, pyqtSignal, QTime
from PyQt5.QtGui import QColor, QConicalGradient, QRadialGradient, QPainter, QBrush, QPen
from PyQt5.QtWidgets import QWidget

class PomodoroTimer(QObject):
    time_changed = pyqtSignal(int)
    state_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.state = "focus"
        self.focus_time = 25 * 60  # 25 minutes
        self.break_time = 5 * 60  # 5 minutes
        self.remaining_time = self.focus_time

    def start(self):
        self.timer.start(1000)  # 1 second interval

    def stop(self):
        self.timer.stop()

    def tick(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.time_changed.emit(self.remaining_time)
        else:
            self.timer.stop()
            if self.state == "focus":
                print("专注时间结束，开始休息")
                self.state = "break"
                self.remaining_time = self.break_time
            else:
                print("休息时间结束，开始专注")
                self.state = "focus"
                self.remaining_time = self.focus_time
            self.state_changed.emit(self.state)
            self.start()

class PomodoroWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.remaining_time = 25 * 60
        self.state = "focus"

    def set_remaining_time(self, remaining_time):
        self.remaining_time = remaining_time
        self.update()

    def set_state(self, state):
        self.state = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 获取窗口大小
        width = self.width()
        height = self.height()
        radius = min(width, height) // 2 - 5  # 减去边框宽度

        # 计算角度
        total_time = 25 * 60 if self.state == "focus" else 5 * 60
        angle = 360 * (1 - self.remaining_time / total_time)

        # 设置渐变颜色
        if self.state == "focus":
            gradient = QConicalGradient(width / 2, height / 2, 90)
            gradient.setColorAt(0, QColor(255, 165, 0))  # 橙色
            gradient.setColorAt(1, QColor(255, 69, 0))  # 深橙色
        else:
            gradient = QRadialGradient(width / 2, height / 2, radius)
            gradient.setColorAt(0, QColor(0, 255, 0))  # 绿色
            gradient.setColorAt(1, QColor(0, 128, 0))  # 深绿色

        # 绘制圆环
        painter.setPen(QPen(QBrush(gradient), 10))
        painter.drawArc(width / 2 - radius, height / 2 - radius, 2 * radius, 2 * radius, 90 * 16, -angle * 16)