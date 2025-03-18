from PyQt5.QtCore import QDate

class Task:
    def __init__(self, date, time, description, urgency):
        self.date = date  # QDate
        self.time = time  # str, e.g., "14:30"
        self.description = description  # str
        self.urgency = urgency  # int, 0~10

    def days_until_due(self):
        """
        返回本任务剩余的天数。

        return this task's remaining days.

        Returns:
            int: 剩余天数。 Remaining days.
        """
        today = QDate.currentDate()
        days_diff = self.date.daysTo(today)
        return days_diff

