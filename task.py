from PyQt5.QtCore import QDate

class Task:
    def __init__(self, date, time, description, urgency):
        self.date = date  # QDate
        self.time = time  # str, e.g., "14:30"
        self.description = description  # str
        self.urgency = urgency  # int, 0~10