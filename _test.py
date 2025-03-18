from PyQt5.QtCore import QObject, QTimer, pyqtSignal, QTime, Qt
from PyQt5.QtGui import QColor, QConicalGradient, QRadialGradient, QPainter, QBrush, QPen, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from win11toast import toast
import global_vars

# 确保在 global_vars 模块中初始化 today_tomatoes
# 示例 global_vars.py 内容：
# today_tomatoes = 0

# 定义番茄钟计时器类
class PomodoroTimer(QObject):
    # 定义信号
    time_changed = pyqtSignal(int)  # 当剩余时间变化时发射
    state_changed = pyqtSignal(str)  # 当状态变化时发射
    notify_signal = pyqtSignal(str, str)  # 用于发送通知

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)  # 创建计时器对象
        self.timer.timeout.connect(self.tick)  # 计时器超时连接到 tick 方法
        self.state = "focus"  # 初始状态为专注
        self.focus_time = 25 * 60  # 专注时间：25 分钟（单位：秒）
        self.break_time = 5 * 60  # 休息时间：5 分钟（单位：秒）
        self.remaining_time = self.focus_time  # 初始剩余时间为专注时间
        self.is_running = False  # 计时器是否正在运行

    def start(self):
        """启动计时器，每秒触发一次"""
        self.timer.start(1000)  # 1000 毫秒 = 1 秒
        self.is_running = True

    def stop(self):
        """停止计时器"""
        self.timer.stop()
        self.is_running = False

    def tick(self):
        """计时器每秒触发的逻辑"""
        if self.remaining_time > 0:
            self.remaining_time -= 1  # 每秒减少 1 秒
            self.time_changed.emit(self.remaining_time)  # 发射时间变化信号
        else:
            self.stop()  # 时间耗尽，停止计时器
            if self.state == "focus":
                # 专注时间结束
                global_vars.today_tomatoes += 1  # 增加今日番茄数
                # 发送通知信号，交由主线程处理
                self.notify_signal.emit("番茄钟时间到咯~", f"今日番茄数：{global_vars.today_tomatoes}\n可选择操作：")
                self.state = "break"  # 切换到休息状态
                self.remaining_time = self.break_time  # 设置休息时间
                self.time_changed.emit(self.remaining_time)  # 更新 UI
            else:
                # 休息时间结束
                self.state = "focus"  # 切换回专注状态
                self.remaining_time = self.focus_time  # 重置为专注时间
                self.state_changed.emit(self.state)  # 发射状态变化信号
                self.start()  # 自动开始新一轮专注

# 定义番茄钟界面类
class PomodoroWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pomodoro_timer = PomodoroTimer(self)  # 创建计时器实例
        self.remaining_time = self.pomodoro_timer.focus_time  # 初始化剩余时间
        self.state = "focus"  # 初始化状态

        # 创建显示时间的标签
        self.time_label = QLabel(self)
        self.time_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        self.time_label.setFont(QFont("Arial", 20))  # 设置字体和大小

        # 创建启动/暂停按钮
        self.start_btn = QPushButton("启动番茄钟", self)
        self.start_btn.clicked.connect(self.toggle_pomodoro)  # 连接点击事件

        # 创建重置按钮，默认隐藏
        self.reset_btn = QPushButton("重置", self)
        self.reset_btn.setVisible(False)
        self.reset_btn.clicked.connect(self.on_reset_clicked)  # 连接重置事件

        # 设置垂直布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.time_label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.reset_btn)

        # 连接计时器信号到界面更新方法
        self.pomodoro_timer.time_changed.connect(self.set_remaining_time)
        self.pomodoro_timer.state_changed.connect(self.set_state)
        self.pomodoro_timer.notify_signal.connect(self.show_notification)
        self.set_remaining_time(self.remaining_time)  # 初始化时间显示

    def toggle_pomodoro(self):
        """切换计时器的启动和暂停状态"""
        if self.pomodoro_timer.is_running:
            self.pomodoro_timer.stop()
            self.start_btn.setText("继续")  # 更新按钮文本
            self.reset_btn.setVisible(True)  # 显示重置按钮
        else:
            self.pomodoro_timer.start()
            self.start_btn.setText("暂停")  # 更新按钮文本
            self.reset_btn.setVisible(False)  # 隐藏重置按钮

    def on_reset_clicked(self):
        """重置计时器到初始状态"""
        self.pomodoro_timer.stop()
        self.pomodoro_timer.state = "focus"  # 重置状态为专注
        self.pomodoro_timer.remaining_time = self.pomodoro_timer.focus_time  # 重置时间
        self.set_remaining_time(self.pomodoro_timer.remaining_time)  # 更新显示
        self.set_state(self.pomodoro_timer.state)  # 更新状态
        self.start_btn.setText("启动番茄钟")  # 重置按钮文本
        self.reset_btn.setVisible(False)  # 隐藏重置按钮

    def set_remaining_time(self, remaining_time):
        """更新剩余时间显示"""
        self.remaining_time = remaining_time
        time_str = QTime(0, 0).addSecs(remaining_time).toString("mm:ss")  # 格式化为 mm:ss
        self.time_label.setText(time_str)
        self.update()  # 触发重绘进度条

    def set_state(self, state):
        """更新状态并触发重绘"""
        self.state = state
        self.update()

    def show_notification(self, title, message):
        """显示通知并处理用户选择"""
        try:
            response = toast(title, message, buttons=["休息\n（默认）", "再专注5分钟", "停止番茄钟"])
            if isinstance(response, dict):
                if response["arguments"] == "http:再专注5分钟":
                    # 用户选择再专注 5 分钟
                    self.pomodoro_timer.stop()
                    self.pomodoro_timer.state = "focus"
                    self.pomodoro_timer.remaining_time = 5 * 60  # 设置 5 分钟
                    self.pomodoro_timer.start()
                    toast("再专注5分钟", "好的喵")  # 确认通知
                elif response["arguments"] == "http:停止番茄钟":
                    # 用户选择停止
                    self.pomodoro_timer.stop()
                    toast("停止了喵", "好的喵")  # 确认通知
        except Exception as e:
            print(f"通知失败: {e}")
            toast("通知出错", "请检查程序运行状态")  # 错误提示

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