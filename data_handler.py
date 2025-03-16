import json
from PyQt5.QtCore import QDate
from task import Task

def save_data(mood_data, tasks, filename="schedule_data.json"):
    data = {
        "mood_data": {date: mood for date, mood in mood_data.items()},
        "tasks": [{"date": task.date.toString(), "time": task.time, "description": task.description, "urgency": task.urgency} for task in tasks]
    }
    with open(filename, "w") as f:
        json.dump(data, f)

def load_data(filename="schedule_data.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            mood_data = {date: mood for date, mood in data["mood_data"].items()}
            tasks = [Task(QDate.fromString(task["date"]), task["time"], task["description"], task["urgency"]) for task in data["tasks"]]
            return mood_data, tasks
    except FileNotFoundError:
        return {}, []