import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit
)
from PyQt5.QtGui import QColor, QPalette, QFont

class TeacherManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Teacher Manager')
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

        # Input box and button for adding a new teacher
        inputLayout = QVBoxLayout()
        self.teacherNameInput = QLineEdit()
        self.teacherNameInput.setPlaceholderText('Enter teacher name...')
        self.addButton = QPushButton('Add Teacher')

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

        inputLayout.addWidget(self.teacherNameInput)
        inputLayout.addWidget(self.addButton)

        # Buttons for update, delete operations
        buttonLayout = QVBoxLayout()
        self.updateButton = QPushButton('Update Teacher')
        self.deleteButton = QPushButton('Delete Teacher')
        buttonLayout.addWidget(self.updateButton)
        buttonLayout.addWidget(self.deleteButton)

        # Set button styles
        self.updateButton.setStyleSheet(button_style)
        self.deleteButton.setStyleSheet(button_style)

        # Table to display teacher names
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(['Teacher Name'])

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
        mainLayout.addLayout(inputLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addWidget(self.table)

        self.setLayout(mainLayout)

        # Connect buttons to functions
        self.updateButton.clicked.connect(self.updateTeacher)
        self.deleteButton.clicked.connect(self.deleteTeacher)
        self.addButton.clicked.connect(self.addTeacher)
        self.table.cellClicked.connect(self.loadRecord)

        # Initialize button states
        self.updateButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.addButton.setEnabled(True)

        # Load data from the database
        self.loadData()

    def loadData(self):
        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()
        c.execute('SELECT DISTINCT teacher FROM timetable')
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_num, row_data in enumerate(rows):
            self.table.setItem(row_num, 0, QTableWidgetItem(row_data[0]))

    def updateTeacher(self):
        currentRow = self.table.currentRow()
        if currentRow < 0:
            QMessageBox.warning(self, 'Error', 'Please select a record to update')
            return

        old_teacher = self.table.item(currentRow, 0).text()
        new_teacher = self.teacherNameInput.text().strip()
        if new_teacher:
            conn = sqlite3.connect('new_timetable.db')
            c = conn.cursor()
            c.execute('UPDATE timetable SET teacher = ? WHERE teacher = ?', (new_teacher, old_teacher))
            conn.commit()
            conn.close()
            self.loadData()
            self.resetInput()
        else:
            QMessageBox.warning(self, 'Error', 'Teacher name cannot be empty')

    def deleteTeacher(self):
        currentRow = self.table.currentRow()
        if currentRow < 0:
            QMessageBox.warning(self, 'Error', 'Please select a record to delete')
            return

        teacher = self.table.item(currentRow, 0).text()
        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()
        c.execute('DELETE FROM timetable WHERE teacher = ?', (teacher,))
        conn.commit()
        conn.close()
        self.loadData()
        self.resetInput()

    def addTeacher(self):
        teacher_name = self.teacherNameInput.text().strip()
        if teacher_name:
            conn = sqlite3.connect('new_timetable.db')
            c = conn.cursor()
            # Insert teacher and set all periods to "None" for each workday
            workdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            periods = ['None'] * 8
            for day in workdays:
                c.execute(
                    'INSERT INTO timetable (teacher, day, period1, period2, period3, period4, period5, period6, period7, period8) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (teacher_name, day, *periods)
                )
            conn.commit()
            conn.close()
            self.teacherNameInput.clear()
            self.loadData()
        else:
            QMessageBox.warning(self, 'Error', 'Teacher name cannot be empty')

    def loadRecord(self, row, column):
        teacher_name = self.table.item(row, column).text()
        self.teacherNameInput.setText(teacher_name)
        self.updateButton.setEnabled(True)
        self.deleteButton.setEnabled(True)
        self.addButton.setEnabled(False)

    def resetInput(self):
        self.teacherNameInput.clear()
        self.updateButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.addButton.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TeacherManager()
    ex.show()
    sys.exit(app.exec_())
