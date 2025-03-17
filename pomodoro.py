from PyQt5.QtCore import QObject, QTimer, pyqtSignal, QTime, Qt
from PyQt5.QtGui import QColor, QConicalGradient, QRadialGradient, QPainter, QBrush, QPen, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from win11toast import toast
from threading import Thread
import global_vars



class PomodoroTimer(QObject):
    time_changed = pyqtSignal(int)
    state_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.state = "focus"
        self.focus_time = 25 * 60  # 默认专注为 25 分钟
        self.break_time = 5 * 60  # 默认休息为 5 分钟
        self.remaining_time = self.focus_time
        self.is_running = False # 是否运行

    def start(self):
        self.timer.start(1000)  # 刷新组件的间隔，1000为1s。
        self.is_running = True

    def stop(self):
        self.timer.stop()
        self.is_running = False

    def pause(self):
        self.timer.stop()
        self.is_running = False

    def tick(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.time_changed.emit(self.remaining_time)
        else:
            self.timer.stop()
            if self.state == "focus":
                print("专注时间结束，开始休息")
                global_vars.today_tomatoes += 1
                Thread(target=lambda : self.toast_up("番茄钟时间到咯~",f"今日番茄数：{global_vars.today_tomatoes}\n可选择操作：") ,daemon=False).start()

            else:
                print("休息时间结束，开始专注")
                self.state = "focus"
                self.remaining_time = self.focus_time
            self.state_changed.emit(self.state)
            self.start()

    def toast_up(self,*args,**kwargs):
        try:
            response = toast(*args,**kwargs,buttons=["休息\n（默认）", "再专注5分钟", "停止番茄钟"])
            if type(response) == dict:
                if response["arguments"] == "http:再专注5分钟":
                    toast("再专注5分钟","好的喵")
                    return
                
                if response["arguments"] == "http:停止番茄钟":
                    toast("停止了喵","好的喵")
                    return
        except Exception as e:
            print(e)
            
        
        toast("开始休息了喵","好的喵")
        self.state = "break"
        self.remaining_time = self.break_time

class PomodoroWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pomodoro_timer = None
        self.remaining_time = 25 * 60
        self.state = "focus"

        # 添加显示剩余时间的标签
        self.time_label = QLabel(self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 20))

        # 添加启动/暂停按钮
        self.start_btn = QPushButton("启动番茄钟", self)
        self.start_btn.clicked.connect(self.toggle_pomodoro)

        # 添加重置按钮
        self.reset_btn = QPushButton("重置", self)
        self.reset_btn.setVisible(False)
        self.reset_btn.clicked.connect(self.on_reset_clicked)  # 假设有一个重置点击事件

        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.time_label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.reset_btn)

        self.set_remaining_time(self.remaining_time)  # 初始化显示时间
        self.pomodoro_timer = None
    def toggle_pomodoro(self):
        if not self.pomodoro_timer:
            return
        
        if self.pomodoro_timer.is_running:
            self.pomodoro_timer.pause()
            self.start_btn.setText("继续")
            self.reset_btn.setVisible(True)
        else:
            self.pomodoro_timer.start()
            self.start_btn.setText("暂停")
            self.reset_btn.setVisible(False)

    def on_reset_clicked(self):
        # 处理重置按钮点击事件
        print("重置按钮被点击")
    def set_remaining_time(self, remaining_time):
        self.remaining_time = remaining_time
        time_str = QTime(0, 0).addSecs(remaining_time).toString("mm:ss")
        self.time_label.setText(time_str)
        self.update()

    def set_state(self, state):
        self.state = state
        self.update()
    def set_timer(self, timer):
        """外部注入计时器实例"""
        self.pomodoro_timer = timer
        self.pomodoro_timer.time_changed.connect(self.set_remaining_time)
        self.pomodoro_timer.state_changed.connect(self.set_state)

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

        if total_time > 0 and self.remaining_time >= 0: # 安全计算时间比例
            progress = 1 - self.remaining_time / total_time
            angle = 360 * progress
        else:
            angle = 0

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