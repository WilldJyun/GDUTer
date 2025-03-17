from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QCalendarWidget, QListWidget, QTableWidget, QMenu, QPushButton, QTableWidgetItem, QMessageBox, QListWidgetItem
from PyQt5.QtCore import Qt, QDate, QPropertyAnimation, QEvent
from PyQt5.QtGui import QTextCharFormat, QColor, QBrush, QPixmap, QPalette, QMouseEvent, QIcon
import json
from task import Task
from dialogs import AddTaskDialog
from pomodoro import PomodoroTimer, PomodoroWidget


class ScheduleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jyun")
        self.setWindowIcon(QIcon("src/favicon.ico"))
        self.setGeometry(100, 100, 2160, 1280)
        self.tasks = []
        self.mood_data = {}
        

        # 初始化番茄钟
        self.pomodoro_timer = PomodoroTimer()
        self.pomodoro_timer.time_changed.connect(self.update_pomodoro_display)
        self.pomodoro_timer.state_changed.connect(self.update_pomodoro_state)

        # 最后
        self.init_ui()
        self.load_data()

    def init_ui(self):
    # 日历
        self.calendar_dock = QDockWidget("日历", self)
        self.calendar = QCalendarWidget()
        self.calendar_dock.setWidget(self.calendar)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.calendar_dock)
        today = QDate.currentDate()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#FFD700"))  # 今日高亮
        self.calendar.setDateTextFormat(today, fmt)
        self.calendar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.calendar.customContextMenuRequested.connect(self.show_mood_menu)

    # Next TODO
        self.todo_dock = QDockWidget("Next TODO", self)
        self.todo_list = QListWidget()
        self.todo_dock.setWidget(self.todo_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.todo_dock)

    # 课程表
        self.course_dock = QDockWidget("课程表", self)
        self.course_table = QTableWidget(12, 7)
        self.course_table.setHorizontalHeaderLabels(["Sun","Mon", "Tue", "Wed", "Thur", "Fri", "Sat"])
        
        Vertical_labels = [
            "第一节\n08:30 - 09:15",
            "第二节\n09:20 - 10:05",
            "第三节\n10:25 - 11:10",
            "第四节\n11:15 - 12:00",
            "第五节\n13:50 - 14:35",
            "第六节\n14:40 - 15:25",
            "第七节\n15:30 - 16:15",
            "第八节\n16:30 - 17:15",
            "第九节\n17:20 - 18:05",
            "第十节\n18:30 - 19:15",
            "第十一节\n19:20 - 20:05",
            "第十二节\n20:10 - 20:55"
        ]
        self.course_table.setVerticalHeaderLabels(Vertical_labels)
        self.course_dock.setWidget(self.course_table)
        self.addDockWidget(Qt.RightDockWidgetArea, self.course_dock)
        # 设置行和列标题文字居中
        self.course_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.course_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)

        # 设置行高以调整行距
        row_height = 55  # 根据需要调整行高
        column_width = 120 # 根据需要调整列宽

        for row in range(max(self.course_table.rowCount(),self.course_table.columnCount())):
            self.course_table.setRowHeight(row, row_height)
            self.course_table.setColumnWidth(row, column_width)


    # 番茄钟
        # 初始化 PomodoroWidget 并传递 PomodoroTimer 实例
        self.pomodoro_widget = PomodoroWidget(self)
        self.pomodoro_widget.set_timer(self.pomodoro_timer)
        
        self.pomodoro_dock = QDockWidget("番茄钟", self)
        self.pomodoro_dock.setWidget(self.pomodoro_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.pomodoro_dock)  # 将番茄钟放在底部
        # connect一下番茄钟状态
        self.pomodoro_timer.time_changed.connect(self.pomodoro_widget.set_remaining_time)
        self.pomodoro_timer.state_changed.connect(self.pomodoro_widget.set_state)

        # 最后，设置摆放位置
        self.splitDockWidget(self.calendar_dock, self.pomodoro_dock, Qt.Vertical)
        self.splitDockWidget(self.todo_dock, self.course_dock, Qt.Vertical)

        # ========== 以上为QWidgets ==========



        # 同步课程到任务
        self.sync_courses_to_tasks()

        # 添加自定义任务按钮
        self.add_task_btn = QPushButton("添加任务", self)
        self.add_task_btn.clicked.connect(self.add_custom_task)
        self.statusBar().addWidget(self.add_task_btn)

        # 透明与背景
        self.setWindowOpacity(1)
        self.background_pixmap = QPixmap('src/background.jpg')
        self.setBackground()

        # 保留其他控件的样式
        self.setStyleSheet("""
            QDockWidget, QListWidget, QTableWidget, QCalendarWidget {
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 150);
                font-family: "Microsoft YaHei";
            }
            QLabel {
                font-family: "Microsoft YaHei";
            }
        """)

    def resizeEvent(self, event):
        # 重写 resizeEvent 方法，窗口大小改变时重新设置背景
        self.setBackground()
        super().resizeEvent(event)

    def setBackground(self):
        # 根据窗口大小调整背景图片大小
        scaled_pixmap = self.background_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        self.setPalette(palette)

    def show_mood_menu(self, pos_or_date):
        if isinstance(pos_or_date, QDate):
            date = pos_or_date
            pos = self.calendar.mapToGlobal(self.calendar.pos())
        else:
            date = self.calendar.selectedDate()
            pos = pos_or_date

        menu = QMenu(self)
        emojis = ["😢", "😔", "😐", "😊", "😍"]
        for i, emoji in enumerate(emojis):
            action = menu.addAction(f"{emoji} ({i})")
            action.triggered.connect(lambda checked, d=date, m=i: self.set_mood(d, m))
        menu.exec_(pos)

    def set_mood(self, date, mood):
        self.mood_data[date.toString()] = mood
        print(f"{date.toString()} 心情设为: {mood}")
        self.save_data()

    def update_todo_list(self):
        self.todo_list.clear()
        sorted_tasks = sorted(self.tasks, key=lambda x: x.urgency, reverse=True)
        for task in sorted_tasks:
            item = QListWidgetItem(f"{task.date.toString()} {task.time} - {task.description} (紧迫度: {task.urgency})")
            green = QColor(0, 255, 0)  # Starting color (green)
            yellow = QColor(255, 255, 0)  # Ending color (yellow)
            t = task.urgency / 10.0  # Interpolation factor (0 to 1)

            # Manually interpolate each color component
            red = int(green.red() * (1 - t) + yellow.red() * t)
            green_val = int(green.green() * (1 - t) + yellow.green() * t)
            blue = int(green.blue() * (1 - t) + yellow.blue() * t)
            alpha = int(green.alpha() * (1 - t) + yellow.alpha() * t)

            # Create the new interpolated color
            color = QColor(red, green_val, blue, alpha)
            item.setBackground(QBrush(color))
            self.todo_list.addItem(item)

    def sync_courses_to_tasks(self):
        for task in self.tasks:
            date = task.date
            times = task.time.split(",")  # 获取节次列表
            desc = task.description
            urgency = task.urgency

            for time in times:
                row = int(time) - 1  # 节次转换为行索引
                col = date.dayOfWeek() - 1  # 日期转换为列索引

                item = QTableWidgetItem(desc)
                item.setBackground(QBrush(self.get_color_by_urgency(urgency)))  # 根据紧迫度设置颜色
                self.course_table.setItem(row, col, item)

        # 示例课程
        # self.course_table.setItem(1, 1, QTableWidgetItem("例子"))

    def get_color_by_urgency(self, urgency):
        # 根据紧迫度返回颜色
        if urgency >= 8:
            return QColor(255, 0, 0)  # 紧迫度高，红色
        elif urgency >= 5:
            return QColor(255, 165, 0)  # 紧迫度中等，橙色
        else:
            return QColor(0, 128, 0)  # 紧迫度低，绿色

    def add_custom_task(self):
        dialog = AddTaskDialog(self)
        if dialog.exec_():
            date_str = dialog.date_input.text()
            time = dialog.time_input.text()
            desc = dialog.desc_input.text()
            urgency = int(dialog.urgency_input.text())
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            if not date.isValid():
                QMessageBox.warning(self, "错误", "无效的日期格式")
                return
            self.tasks.append(Task(date, time, desc, urgency))
            self.update_todo_list()
            self.save_data()

    def save_data(self):
        data = {
            "mood_data": {date: mood for date, mood in self.mood_data.items()},
            "tasks": [{"date": task.date.toString(), "time": task.time, "description": task.description, "urgency": task.urgency} for task in self.tasks]
        }
        with open("data.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        try:
            with open("data.json", "r", encoding='utf-8') as f:
                data = json.load(f)
                self.mood_data = {date: mood for date, mood in data["mood_data"].items()}
                self.tasks = [
                    Task(QDate.fromString(task["date"], "yyyy-MM-dd"),
                    task["time"], 
                    task["description"], 
                    task["urgency"])
                    for task in data["tasks"]
                ]
                self.update_todo_list()
                self.sync_courses_to_tasks()  # 同步课程到任务
        except FileNotFoundError:
            pass
    def showEvent(self, event):
        print(f"窗口位置和大小: {self.geometry()}")
        super().showEvent(event)

    def start_pomodoro(self):  # 番茄钟计时启动
        self.pomodoro_timer.start()

    def update_pomodoro_display(self, remaining_time):
        # 更新番茄钟显示
        self.pomodoro_widget.set_remaining_time(remaining_time)

    def update_pomodoro_state(self, state):
        # 更新番茄钟状态
        self.pomodoro_widget.set_state(state)