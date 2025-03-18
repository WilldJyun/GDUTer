# 导入必要的 PyQt5 模块和其他依赖项
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QCalendarWidget, QListWidget, QWidget, QLabel, QHBoxLayout, QTableWidget, QMenu, QPushButton, QTableWidgetItem, QMessageBox, QListWidgetItem
from PyQt5.QtCore import Qt, QDate, QPropertyAnimation, QEvent
from PyQt5.QtGui import QTextCharFormat, QColor, QBrush, QPixmap, QPalette, QMouseEvent, QIcon
import json
from task import Task  # 自定义任务类
from dialogs import AddTaskDialog  # 添加任务对话框
from pomodoro import PomodoroTimer, PomodoroWidget  # 番茄钟相关模块


class ScheduleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jyun")  # 设置窗口标题
        self.setWindowIcon(QIcon("src/favicon.ico"))  # 设置窗口图标
        self.setGeometry(100, 100, 2160, 1280)  # 设置窗口初始位置和大小
        self.tasks = []  # 初始化任务列表
        self.mood_data = {}  # 初始化心情数据字典

        # 初始化番茄钟计时器
        self.pomodoro_timer = PomodoroTimer()
        self.pomodoro_timer.time_changed.connect(self.update_pomodoro_display)  # 连接时间变化信号
        self.pomodoro_timer.state_changed.connect(self.update_pomodoro_state)  # 连接状态变化信号

        # 初始化用户界面并加载数据
        self.init_ui()
        self.load_data()

    def init_ui(self):
        # 日历控件初始化
        self.calendar_dock = QDockWidget("日历", self)  # 创建日历停靠窗口
        self.calendar = QCalendarWidget()  # 创建日历小部件
        self.calendar_dock.setWidget(self.calendar)  # 设置日历小部件到停靠窗口
        self.addDockWidget(Qt.LeftDockWidgetArea, self.calendar_dock)  # 将日历停靠窗口添加到左侧区域
        today = QDate.currentDate()  # 获取当前日期
        fmt = QTextCharFormat()  # 创建文本格式对象
        fmt.setBackground(QColor("#FFD700"))  # 设置高亮背景颜色
        self.calendar.setDateTextFormat(today, fmt)  # 设置当前日期的高亮样式
        self.calendar.setContextMenuPolicy(Qt.CustomContextMenu)  # 启用自定义右键菜单
        self.calendar.customContextMenuRequested.connect(self.show_mood_menu)  # 连接右键菜单信号

        # Next TODO 列表初始化
        self.todo_dock = QDockWidget("Next TODO", self)  # 创建待办事项停靠窗口
        self.todo_widget = QWidget()  # 创建待办事项主控件
        self.todo_layout = QHBoxLayout(self.todo_widget)  # 创建水平布局

        self.todo_list = QListWidget()  # 创建待办事项列表
        self.todo_layout.addWidget(self.todo_list)  # 将待办事项列表添加到布局中

        self.task_countdown_label = QLabel("最紧急任务倒计时: ")  # 创建任务倒计时标签
        self.todo_layout.addWidget(self.task_countdown_label)  # 将标签添加到布局中
        self.todo_widget.layout().setStretchFactor(self.todo_list, 1)  # 设置列表拉伸因子
        self.todo_widget.layout().setStretchFactor(self.task_countdown_label, 1)  # 设置标签拉伸因子

        self.todo_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.todo_list.customContextMenuRequested.connect(self.show_todo_menu) # 给列表添加右键操作

        self.todo_dock.setWidget(self.todo_widget)  # 设置待办事项主控件到停靠窗口
        self.addDockWidget(Qt.RightDockWidgetArea, self.todo_dock)  # 将待办事项停靠窗口添加到右侧区域

        # 日程表初始化
        self.course_dock = QDockWidget("日程表", self)  # 创建日程表停靠窗口
        self.course_table = QTableWidget(12, 7)  # 创建日程表表格 (12行7列)
        self.course_table.setHorizontalHeaderLabels(["Sun","Mon", "Tue", "Wed", "Thur", "Fri", "Sat"])  # 设置列标题

        Vertical_labels = [  # 定义日程时间段标签
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
        self.course_table.setVerticalHeaderLabels(Vertical_labels)  # 设置行标题
        self.course_dock.setWidget(self.course_table)  # 设置日程表到停靠窗口
        self.addDockWidget(Qt.RightDockWidgetArea, self.course_dock)  # 将日程表停靠窗口添加到右侧区域

        # 设置日程表行和列标题文字居中
        self.course_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.course_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)

        # 设置日程表行高和列宽
        row_height = 55  # 行高
        column_width = 120  # 列宽
        for row in range(max(self.course_table.rowCount(), self.course_table.columnCount())):
            self.course_table.setRowHeight(row, row_height)
            self.course_table.setColumnWidth(row, column_width)

        # 番茄钟初始化
        self.pomodoro_widget = PomodoroWidget(self)  # 创建番茄钟小部件
        self.pomodoro_widget.set_timer(self.pomodoro_timer)  # 设置番茄钟计时器实例

        self.pomodoro_dock = QDockWidget("番茄钟", self)  # 创建番茄钟停靠窗口
        self.pomodoro_dock.setWidget(self.pomodoro_widget)  # 设置番茄钟小部件到停靠窗口
        self.addDockWidget(Qt.BottomDockWidgetArea, self.pomodoro_dock)  # 将番茄钟停靠窗口添加到底部区域

        # 连接番茄钟信号
        self.pomodoro_timer.time_changed.connect(self.pomodoro_widget.set_remaining_time)
        self.pomodoro_timer.state_changed.connect(self.pomodoro_widget.set_state)

        # 设置停靠窗口摆放位置
        self.splitDockWidget(self.calendar_dock, self.pomodoro_dock, Qt.Vertical)
        self.splitDockWidget(self.todo_dock, self.course_dock, Qt.Vertical)

        # 同步日程到任务
        self.sync_courses_to_table()

        # 添加自定义任务按钮
        self.add_task_btn = QPushButton("添加任务", self)  # 创建添加任务按钮
        self.add_task_btn.clicked.connect(self.add_custom_task)  # 连接按钮点击信号
        self.statusBar().addWidget(self.add_task_btn)  # 将按钮添加到状态栏

        # 设置窗口透明度和背景图片
        self.setWindowOpacity(1)
        self.background_pixmap = QPixmap('src/background.jpg')  # 加载背景图片
        self.setBackground()

        # 设置控件样式
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

    # 窗口大小改变时重新设置背景
    def resizeEvent(self, event):
        self.setBackground()
        super().resizeEvent(event)

    # 根据窗口大小调整背景图片
    def setBackground(self):
        scaled_pixmap = self.background_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        self.setPalette(palette)

# ==========================  日历与心情 CALENDAR & MOOD widgets ==========================
    # 显示心情菜单
    def show_mood_menu(self, pos_or_date):
        if isinstance(pos_or_date, QDate):
            date = pos_or_date
            pos = self.calendar.mapToGlobal(self.calendar.pos())
        else:
            date = self.calendar.selectedDate()
            pos = pos_or_date

        menu = QMenu(self)  # 创建右键菜单
        emojis = ["😢", "😔", "😐", "😊", "😍"]  # 定义表情选项
        for i, emoji in enumerate(emojis):
            action = menu.addAction(f"{emoji} ({i})")  # 添加表情选项
            action.triggered.connect(lambda checked, d=date, m=i: self.set_mood(d, m))  # 连接选项触发信号
        menu.exec_(pos)  # 显示菜单

    # 设置心情数据
    def set_mood(self, date, mood):
        self.mood_data[date.toString()] = mood  # 更新心情数据
        print(f"{date.toString()} 心情设为: {mood}")
        self.save_data()  # 保存数据

# ==========================  代办任务 Task TODO widgets ==========================
    # 更新待办事项列表
    def update_todo_list(self):
        self.todo_list.clear()  # 清空列表

        # 按紧迫度排序任务
        sorted_tasks = sorted(self.tasks, key=lambda x: x.urgency, reverse=True)  

        for task in sorted_tasks:
            item = QListWidgetItem(f"{task.date.toString()} {task.time} - {task.description} (紧迫度: {task.urgency})")
            green = QColor(0, 233, 0)  # 起始颜色 (绿色)
            yellow = QColor(233, 0, 0)  # 结束颜色 (黄色)
            t = task.urgency / 10.0  # 插值因子 (0到1)

            # 手动插值每个颜色分量
            red = int(green.red() * (1 - t) + yellow.red() * t)
            green_val = int(green.green() * (1 - t) + yellow.green() * t)
            blue = int(green.blue() * (1 - t) + yellow.blue() * t)
            alpha = int(green.alpha() * (1 - t) + yellow.alpha() * t)

            # 创建新的插值颜色
            color = QColor(red, green_val, blue, alpha)
            item.setBackground(QBrush(color))  # 设置背景颜色
            self.todo_list.addItem(item)  # 添加到列表中
        
        if sorted_tasks:
            most_urgent_task = sorted_tasks[0]
            days_left = most_urgent_task.days_until_due()
            if days_left > 1:
                self.task_countdown_label.setText(f"最紧急任务倒计时: {most_urgent_task.description} (紧迫度: {most_urgent_task.urgency})")
            else:
                self.task_countdown_label.setText(f"最紧急任务倒计时: {days_left}天 {most_urgent_task.time} - {most_urgent_task.description} (紧迫度: {most_urgent_task.urgency})")
        else:
            self.task_countdown_label.setText("最紧急任务倒计时: 无任务")

    # 同步日程到日程表
    def sync_courses_to_table(self):
        for task in self.tasks:
            date = task.date
            times = task.time.split(",")  # 获取节次列表
            desc = task.description
            urgency = task.urgency

            for time in times:
                row = int(time) - 1  # 节次转换为行索引
                col = date.dayOfWeek() - 1  # 日期转换为列索引

                item = QTableWidgetItem(desc)  # 创建表格项
                item.setBackground(QBrush(self.get_color_by_urgency(urgency)))  # 根据紧迫度设置颜色
                self.course_table.setItem(row, col, item)  # 设置表格项

    # 根据紧迫度返回颜色
    def get_color_by_urgency(self, urgency):
        if urgency >= 8:
            return QColor(255, 0, 0)  # 紧迫度高，红色
        elif urgency >= 5:
            return QColor(255, 165, 0)  # 紧迫度中等，橙色
        else:
            return QColor(0, 128, 0)  # 紧迫度低，绿色

    # 添加自定义任务
    def add_custom_task(self):
        dialog = AddTaskDialog(self)  # 创建添加任务对话框
        if dialog.exec_():
            date_str = dialog.date_input.text()  # 获取日期输入
            time = dialog.time_input.text()  # 获取时间输入
            desc = dialog.desc_input.text()  # 获取描述输入
            urgency = int(dialog.urgency_input.text())  # 获取紧迫度输入
            date = QDate.fromString(date_str, "yyyy-MM-dd")  # 转换日期字符串为 QDate 对象
            if not date.isValid():  # 验证日期有效性
                QMessageBox.warning(self, "错误", "无效的日期格式")
                return
            self.tasks.append(Task(date, time, desc, urgency))  # 添加任务到任务列表
            self.update_todo_list()  # 更新待办事项列表
            self.save_data()  # 保存数据

    # 待办事项的右键菜单
    def show_todo_menu(self, pos):
        menu = QMenu(self)
        delete_action = menu.addAction("删除") # 添加删除选项
        delete_action.triggered.connect(self.delete_task) # 连接信号
        menu.exec_(self.todo_list.mapToGlobal(pos)) # 显示菜单

    # 删除菜单功能
    def delete_task(self):
        selected_items = self.todo_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择要删除的任务")
            return

        for item in selected_items:
            task_description = item.text().split(" - ")[1].split(" (")[0]
            task_to_remove = next((task for task in self.tasks if task.description == task_description), None)
            if task_to_remove:
                self.tasks.remove(task_to_remove)
                self.update_todo_list()
                self.sync_courses_to_table()
                self.save_data()

# ========================== 保存数据操作 Save data ==========================
    # 保存数据到文件
    def save_data(self):
        data = {
            "mood_data": {date: mood for date, mood in self.mood_data.items()},
            "tasks": [{"date": task.date.toString(), "time": task.time, "description": task.description, "urgency": task.urgency} for task in self.tasks]
        }
        with open("data.json", "w") as f:
            json.dump(data, f)

    # 从文件加载数据
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
                self.sync_courses_to_table()  # 同步日程到任务
        except FileNotFoundError:
            pass

# ==========================  番茄钟 Pomodoro widgets ==========================

    # 启动番茄钟计时
    def start_pomodoro(self):
        self.pomodoro_timer.start()

    # 更新番茄钟显示
    def update_pomodoro_display(self, remaining_time):
        self.pomodoro_widget.set_remaining_time(remaining_time)

    # 更新番茄钟状态
    def update_pomodoro_state(self, state):
        self.pomodoro_widget.set_state(state)

# ==========================  其他 Others ==========================
    # 调试，显示窗口信息
    def showEvent(self, event):
        print(f"窗口位置和大小: {self.geometry()}")
        super().showEvent(event)

