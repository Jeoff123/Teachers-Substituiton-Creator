import sys
import sqlite3
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QScrollArea, QFormLayout, QComboBox
)
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt
from teacher_manager import TeacherManager

class TimeTableManager(QWidget):
    def __init__(self):
        super().__init__()
        self.checkboxes = {}  # Initialize self.checkboxes
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Timetable Manager')
        self.setGeometry(100, 100, 1000, 800)

        # Set color palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor('#ffffff'))  # Background color
        palette.setColor(QPalette.Button, QColor('#0288d1'))  # Button color
        palette.setColor(QPalette.ButtonText, QColor('#000000'))  # Button text color
        palette.setColor(QPalette.Text, QColor('#000000'))  # Text color
        self.setPalette(palette)

        # Set font
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

        # Main layout
        mainLayout = QVBoxLayout()

        # Dropdown for selecting the day
        self.dayComboBox = QComboBox()
        self.dayComboBox.addItems(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        self.dayComboBox.currentIndexChanged.connect(self.updateTable)
        self.dayComboBox.setStyleSheet("font-size: 16px;")

        # Scroll area for checkboxes
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.checkboxWidget = QWidget()
        self.scrollArea.setWidget(self.checkboxWidget)
        self.checkboxLayout = QFormLayout(self.checkboxWidget)

        # Button to process substitutions
        self.processButton = QPushButton('Process Substitutions')
        self.processButton.clicked.connect(self.processSubstitutions)
        self.processButton.setStyleSheet("""
            QPushButton {
                background-color: #0288d1;
                color: #ffffff;
                padding: 10px 20px;
                font-size: 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0277bd;
            }
        """)

        # Button to open Schedule Manager
        self.openScheduleManagerButton = QPushButton('Open Schedule Manager')
        self.openScheduleManagerButton.clicked.connect(self.openScheduleManager)
        self.openScheduleManagerButton.setStyleSheet("""
            QPushButton {
                background-color: #0288d1;
                color: #ffffff;
                padding: 10px 20px;
                font-size: 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0277bd;
            }
        """)

        # Button to open Teacher Manager
        self.openTeacherManagerButton = QPushButton('Open Teacher Manager')
        self.openTeacherManagerButton.clicked.connect(self.openTeacherManager)
        self.openTeacherManagerButton.setStyleSheet("""
            QPushButton {
                background-color: #0288d1;
                color: #ffffff;
                padding: 10px 20px;
                font-size: 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0277bd;
            }
        """)

        # Table to display timetable data
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Day', 'Teacher', 'Period 1', 'Period 2', 'Period 3', 'Period 4',
            'Period 5', 'Period 6', 'Period 7', 'Period 8'
        ])

        # Set table colors and font
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #e0f2f1;  # Table background color
                gridline-color: #004d40;    # Table grid color
            }
            QHeaderView::section {
                background-color: #004d40;  # Header background color
                color: #ffffff;            # Header text color
                font-size: 16px;
            }
            QTableWidget::item {
                padding: 10px;
                border: 1px solid #004d40;  # Cell border color
                font-size: 14px;
            }
        """)
        self.table.setFont(QFont('Arial', 12))

        # Add widgets to layout
        mainLayout.addWidget(self.dayComboBox)
        mainLayout.addWidget(self.scrollArea)
        mainLayout.addWidget(self.processButton)
        mainLayout.addWidget(self.openScheduleManagerButton)
        mainLayout.addWidget(self.openTeacherManagerButton)
        mainLayout.addWidget(self.table)

        self.setLayout(mainLayout)

        # Initial table load for the first day
        self.updateTable()

    def loadAbsentees(self):
        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()
        c.execute('SELECT DISTINCT teacher FROM timetable')
        rows = c.fetchall()
        conn.close()

        # Save the state of the currently selected checkboxes
        checked_states = {teacher: checkbox.isChecked() for teacher, checkbox in self.checkboxes.items() if checkbox}

        # Clear old checkboxes
        for i in reversed(range(self.checkboxLayout.count())):
            widget = self.checkboxLayout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Create new checkboxes
        self.checkboxes = {}
        for row in rows:
            teacher_name = row[0]
            checkbox = QCheckBox(teacher_name)
            checkbox.setStyleSheet("font-size: 16px;")
            self.checkboxLayout.addWidget(checkbox)
            self.checkboxes[teacher_name] = checkbox

        # Restore the state of the checkboxes
        for teacher, is_checked in checked_states.items():
            if teacher in self.checkboxes:
                self.checkboxes[teacher].setChecked(is_checked)

    def updateTable(self):
        day = self.dayComboBox.currentText()
        self.loadAbsentees()  # Reload absentees checkboxes
        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()
        c.execute('SELECT * FROM timetable WHERE day = ?', (day,))
        rows = c.fetchall()
        self.table.setRowCount(len(rows))
        for row_num, row_data in enumerate(rows):
            for col_num, col_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
        conn.close()

    def processSubstitutions(self):
        day = self.dayComboBox.currentText()
        absentees = [teacher for teacher, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        if not absentees:
            QMessageBox.warning(self, 'Error', 'Please select at least one absentee')
            return

        updated_tt = self.create_time_table(day, absentees)
        self.displayUpdatedTimetable(updated_tt)

    def create_time_table(self, day, absentees):
        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()

        # Fetch timetable data for the specified day
        c.execute('SELECT * FROM timetable WHERE day = ?', (day,))
        rows = c.fetchall()
        timetable = {}
        for row in rows:
            timetable[row[2]] = row[3:]  # teacher -> periods

        # Identify presentees (teachers who are not absent)
        presentees = {teacher for teacher in timetable if teacher not in absentees}

        # Prepare a structure for periods replacement
        periods = {i: [] for i in range(8)}
        for teacher in presentees:
            for i, period in enumerate(timetable[teacher]):
                if period.upper() == 'FREE':
                    periods[i].append(teacher)

        # Substitute periods for absentees
        for teacher in absentees:
            if teacher in timetable:
                for i, period in enumerate(timetable[teacher]):
                    if period.upper() != 'FREE' and periods[i]:
                        replacement_teacher = random.choice(periods[i])
                        timetable[replacement_teacher] = (
                                timetable[replacement_teacher][:i] + (period,) + timetable[replacement_teacher][i + 1:]
                        )

                # Remove absent teacher's record
                del timetable[teacher]

        conn.close()
        return timetable

    def displayUpdatedTimetable(self, updated_tt):
        self.table.setRowCount(len(updated_tt))
        row_num = 0
        for teacher, periods in updated_tt.items():
            row_data = [None] * 11
            row_data[1] = self.dayComboBox.currentText()  # Day
            row_data[2] = teacher  # Teacher
            row_data[3:11] = periods  # Periods
            for col_num, col_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
            row_num += 1

        # Add day and absentee names above the table
        self.table.setVerticalHeaderLabels([
            f'{self.dayComboBox.currentText()} - Absentees: {", ".join([teacher for teacher, checkbox in self.checkboxes.items() if checkbox.isChecked()])}'
        ] * len(updated_tt))  # Setting the header labels

    def openScheduleManager(self):
        self.schedule_manager = ScheduleManager()
        self.schedule_manager.show()

    def openTeacherManager(self):
        self.teacher_manager = TeacherManager()
        self.teacher_manager.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimeTableManager()
    window.show()
    sys.exit(app.exec_())
