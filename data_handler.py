import json
from PyQt5.QtCore import QDate
from task import Task
import global_vars
def save_data(mood_data, tasks, filename = global_vars.data_file_name):
    data = {
        "last_opened": QDate.currentDate().toString(),
        "last_daily_tomatoes_clockes_routines": global_vars.today_tomatoes,
        "total_tomatoes": global_vars.total_tomatoes,
        "mood_data": {date: mood for date, mood in mood_data.items()},
        "tasks": [{"date": task.date.toString(), "time": task.time, "description": task.description, "urgency": task.urgency} for task in tasks]
        }
    with open(filename, "w") as f:
        json.dump(data, f)
    
    print("所有数据已保存到", filename)
    

def load_data(filename = global_vars.data_file_name):
    try:
        with open(filename, "r") as f:
            data = json.load(f)

            # 自动处理更新番茄钟记录，保证每日番茄钟数量正确
            last_opened = QDate.fromString(data["last_opened"])
            last_daily_tomatoes_clockes_routines = data["last_daily_tomatoes_clockes_routines"]
            if last_opened.daysTo(QDate.currentDate()) == 0:
                global_vars.today_tomatoes = last_daily_tomatoes_clockes_routines
            else:
                global_vars.today_tomatoes = 0
            global_vars.total_tomatoes = data["total_tomatoes"]


            # 处理日期对应情绪
            mood_data = {date: mood for date, mood in data["mood_data"].items()}

            # 处理任务
            tasks = [Task(QDate.fromString(task["date"]), task["time"], task["description"], task["urgency"]) for task in data["tasks"]]
            
            # 最后，调试输出加载到的东西，并返回
            print("Loaded data:")
            print("Last opened:", last_opened.toString())
            print("Last daily tomatoes clocked routines:", last_daily_tomatoes_clockes_routines)
            print("Total tomatoes:", global_vars.total_tomatoes)
            print("Mood data:", mood_data)
            print("Tasks:", tasks)
            return mood_data, tasks
    except FileNotFoundError:
        return {}, []