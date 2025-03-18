from PyQt5.QtCore import QObject, QTimer, pyqtSignal, QTime, Qt
from PyQt5.QtGui import QColor, QConicalGradient, QRadialGradient, QPainter, QBrush, QPen, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from win11toast import toast
import threading
import global_vars
import asyncio

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
        self.pomodoro_widget = None # 引用pomodoro_widget

    def set_selfwidget(self, selfwidget):
        self.pomodoro_widget = selfwidget

    def start(self):
        """启动计时器，每秒触发一次"""
        self.timer.start(1000)  # 刷新组件的间隔，1000为1s。
        self.is_running = True

    def stop(self):
        """停止计时器"""
        self.timer.stop()
        self.is_running = False

    
    def tick(self): 
        """计时器每秒触发的逻辑"""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.time_changed.emit(self.remaining_time)
        else:
            self.timer.stop()
            if self.state == "focus":
                print("专注时间结束，开始休息")
                global_vars.total_tomatoes += 1
                global_vars.today_tomatoes += 1
                self.remaining_time = self.break_time
                self.time_changed.emit(self.remaining_time)
                if global_vars.today_tomatoes % 2 == 0: # 如果是偶数，说明两个番茄钟，一小时了，提醒喝水
                    title,content = global_vars.random_focus_timeup_prompt(healthy_remind=True)
                    self.toast_up(title, content + "\n可选择操作：")
                else:
                    title,content = global_vars.random_focus_timeup_prompt(healthy_remind=False)
                    self.toast_up(title, content + "\n可选择操作：")

            else:
                print("休息时间结束，开始专注")
                title, content, user_response = global_vars.random_break_timeup_prompt()
                async def async_toast(*args,**kwargs):
                    return await toast(*args,**kwargs)
                asyncio.run(async_toast(title, content, buttons=[user_response]))
                
                self.state = "focus"
                self.remaining_time = self.focus_time
                self.state_changed.emit(self.state)
                self.start()

    def toast_up(self,*args,**kwargs):
        try:
            response = toast(*args,**kwargs,buttons=["休息\n（默认）", "再专注5分钟", "停止番茄钟"])
            if type(response) == dict:
                if response["arguments"] == "http:再专注5分钟":
                    print("再专注5分钟")
                    global_vars.total_tomatoes -= 1 # 总的减去一个番茄钟，因为再专注五分钟仍然是原来的番茄钟。
                    global_vars.today_tomatoes -= 1 # 今日减去一个番茄钟，因为再专注五分钟仍然是原来的番茄钟。
                    
                    self.state = "focus"
                    self.remaining_time = 5*60 # 5分钟
                    self.state_changed.emit(self.state)
                    self.start()
                    return
                
                if response["arguments"] == "http:停止番茄钟":
                    print("番茄钟停止了")
                    self.pomodoro_widget.on_reset_clicked()
                    return
        except Exception as e:
            print("番茄钟处理发生错误！")
            raise e
        
        # 默认选项放下面自动处理
        
        print("开始休息")
        self.state = "break"
        self.state_changed.emit(self.state)
        self.remaining_time = self.break_time
        self.start()
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
            self.pomodoro_timer.stop()
            self.start_btn.setText("继续")
            self.reset_btn.setVisible(True)
        else:
            self.pomodoro_timer.start()
            self.start_btn.setText("暂停")
            self.reset_btn.setVisible(False)

    def on_reset_clicked(self):
        """重置计时器到初始状态"""
        print("重置按钮被点击")

        self.pomodoro_timer.stop()
        self.pomodoro_timer.state = "focus"  # 重置状态为专注
        self.pomodoro_timer.remaining_time = self.pomodoro_timer.focus_time  # 重置时间
        self.set_remaining_time(self.pomodoro_timer.remaining_time)  # 更新显示
        self.set_state(self.pomodoro_timer.state)  # 更新状态
        self.start_btn.setText("启动番茄钟")  # 重置按钮文本
        self.reset_btn.setVisible(False)  # 隐藏重置按钮
    def set_remaining_time(self, remaining_time):
        self.remaining_time = remaining_time
        time_str = QTime(0, 0).addSecs(remaining_time).toString("mm:ss")
        self.time_label.setText(time_str)
        self.update()

    def set_state(self, state):
        self.state = state
        self.update()
    def set_timer(self, timer):
        """外部注入计时器实例，同时为pomodoro_time也注入pomodoro_widget自己，方便引用方法。"""
        self.pomodoro_timer = timer
        self.pomodoro_timer.time_changed.connect(self.set_remaining_time)
        self.pomodoro_timer.state_changed.connect(self.set_state)
        self.pomodoro_timer.set_selfwidget(self)

    def paintEvent(self, event):
        """绘制进度条圆环"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿

        width = self.width()
        height = self.height() - 50  # 留出底部按钮空间
        radius = min(width, height) // 2 - 5  # 计算圆环半径

        # 根据状态获取总时间
        total_time = self.pomodoro_timer.focus_time if self.state == "focus" else self.pomodoro_timer.break_time
        if total_time > 0 and self.remaining_time >= 0:
            progress = 1 - self.remaining_time / total_time  # 计算进度
            angle = 360 * progress  # 转换为角度
        else:
            angle = 0

        # 根据状态设置渐变颜色
        if self.state == "focus":
            gradient = QConicalGradient(width / 2, height / 2, 90)  # 锥形渐变
            gradient.setColorAt(0, QColor(255, 165, 0))  # 橙色
            gradient.setColorAt(1, QColor(255, 69, 0))  # 深橙色
        else:
            gradient = QRadialGradient(width / 2, height / 2, radius)  # 径向渐变
            gradient.setColorAt(0, QColor(0, 255, 0))  # 绿色
            gradient.setColorAt(1, QColor(0, 128, 0))  # 深绿色

        # 绘制圆环
        painter.setPen(QPen(QBrush(gradient), 10))  # 设置画笔宽度为 10
        painter.drawArc(width / 2 - radius, height / 2 - radius, 2 * radius, 2 * radius, 90 * 16, -angle * 16)