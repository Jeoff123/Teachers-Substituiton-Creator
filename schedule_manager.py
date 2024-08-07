import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt

class ScheduleManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Schedule Manager')
        self.setGeometry(100, 100, 800, 600)

        # Set color palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor('#ffffff'))  # Background color
        palette.setColor(QPalette.Button, QColor('#0288d1'))  # Button color
        palette.setColor(QPalette.ButtonText, QColor('#000000'))  # Button text color (black)
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
        mainLayout.addWidget(self.dayComboBox)

        # Form layout for schedule input
        formLayout = QFormLayout()

        # Uneditable text box for teacher name
        self.teacherLineEdit = QLineEdit()
        self.teacherLineEdit.setReadOnly(True)
        formLayout.addRow('Teacher Name:', self.teacherLineEdit)

        # Period inputs
        self.periodInputs = []
        for i in range(8):  # Assuming 8 periods
            periodInput = QLineEdit()
            formLayout.addRow(f'Period {i + 1}:', periodInput)
            self.periodInputs.append(periodInput)

        # Buttons for add, update, delete operations
        buttonLayout = QVBoxLayout()
        self.addButton = QPushButton('Add Schedule')
        self.updateButton = QPushButton('Update Schedule')
        self.deleteButton = QPushButton('Delete Schedule')
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.updateButton)
        buttonLayout.addWidget(self.deleteButton)

        # Set button styles
        button_style = """
            QPushButton {
                background-color: #0288d1;  # Button background color
                color: #000000;  # Button text color (black)
                padding: 10px;
                font-size: 16px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0277bd;  # Darker button background color on hover
            }
        """
        self.addButton.setStyleSheet(button_style)
        self.updateButton.setStyleSheet(button_style)
        self.deleteButton.setStyleSheet(button_style)

        # Table to display schedule data
        self.table = QTableWidget()
        self.table.setColumnCount(11)  # Assuming 1 ID, 1 Day, 1 Teacher, and 8 periods
        self.table.setHorizontalHeaderLabels(['ID', 'Day', 'Teacher', 'Period 1', 'Period 2', 'Period 3', 'Period 4', 'Period 5', 'Period 6', 'Period 7', 'Period 8'])

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
        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addWidget(self.table)

        self.setLayout(mainLayout)

        # Connect buttons to functions
        self.addButton.clicked.connect(self.addSchedule)
        self.updateButton.clicked.connect(self.updateSchedule)
        self.deleteButton.clicked.connect(self.deleteSchedule)
        self.table.cellClicked.connect(self.loadRecord)
        self.dayComboBox.currentIndexChanged.connect(self.loadData)

        # Load data from the database
        self.loadData()

    def loadData(self):
        day = self.dayComboBox.currentText()
        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()
        c.execute('SELECT * FROM timetable WHERE day = ?', (day,))
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_num, row_data in enumerate(rows):
            for col_num, col_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def addSchedule(self):
        day = self.dayComboBox.currentText()
        teacher = self.teacherLineEdit.text()
        periods = [input.text() for input in self.periodInputs]
        if not day or not teacher or any(not period for period in periods):
            QMessageBox.warning(self, 'Error', 'All fields must be filled')
            return

        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()
        c.execute('INSERT INTO timetable (day, teacher, period1, period2, period3, period4, period5, period6, period7, period8) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (day, teacher, *periods))
        conn.commit()
        conn.close()
        self.loadData()
        self.clearInputs()

    def updateSchedule(self):
        currentRow = self.table.currentRow()
        if currentRow < 0:
            QMessageBox.warning(self, 'Error', 'Please select a record to update')
            return

        id_ = self.table.item(currentRow, 0).text()
        day = self.dayComboBox.currentText()
        teacher = self.teacherLineEdit.text()
        periods = [input.text() for input in self.periodInputs]
        if not day or not teacher or any(not period for period in periods):
            QMessageBox.warning(self, 'Error', 'All fields must be filled')
            return

        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()
        c.execute('UPDATE timetable SET day = ?, teacher = ?, period1 = ?, period2 = ?, period3 = ?, period4 = ?, period5 = ?, period6 = ?, period7 = ?, period8 = ? WHERE id = ?',
                  (day, teacher, *periods, id_))
        conn.commit()
        conn.close()
        self.loadData()
        self.clearInputs()

    def deleteSchedule(self):
        currentRow = self.table.currentRow()
        if currentRow < 0:
            QMessageBox.warning(self, 'Error', 'Please select a record to delete')
            return

        id_ = self.table.item(currentRow, 0).text()
        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()
        c.execute('DELETE FROM timetable WHERE id = ?', (id_,))
        conn.commit()
        conn.close()
        self.loadData()
        self.clearInputs()

    def loadRecord(self, row, column):
        day = self.table.item(row, 1).text()
        teacher = self.table.item(row, 2).text()
        self.dayComboBox.setCurrentText(day)
        self.teacherLineEdit.setText(teacher)
        for i in range(8):
            self.periodInputs[i].setText(self.table.item(row, i + 3).text())

    def clearInputs(self):
        self.dayComboBox.setCurrentIndex(0)
        self.teacherLineEdit.clear()
        for input in self.periodInputs:
            input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScheduleManager()
    ex.show()
    sys.exit(app.exec_())
