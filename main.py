import sys
from PyQt5.QtWidgets import QApplication
from schedule_app import ScheduleApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec_())