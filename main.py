import sys
import sqlite3
import random
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QScrollArea, QFormLayout, QComboBox, QFileDialog
)
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt, QTimer
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from teacher_manager import TeacherManager
from schedule_manager import ScheduleManager


class TimeTableManager(QWidget):
    def __init__(self):
        super().__init__()
        self.checkboxes = {}
        self.teacher_manager = None  # Initialize teacher_manager
        self.schedule_manager = None  # Initialize schedule_manager
        self.init_ui()
        self.setup_timer()  # Setup the timer for automatic updates

    def init_ui(self):
        self.setWindowTitle('Timetable Manager')
        self.setGeometry(100, 100, 1000, 800)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor('#ffffff'))
        palette.setColor(QPalette.Button, QColor('#0288d1'))
        palette.setColor(QPalette.ButtonText, QColor('#000000'))
        palette.setColor(QPalette.Text, QColor('#000000'))
        self.setPalette(palette)

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

        main_layout = QVBoxLayout()

        self.day_combo_box = QComboBox()
        self.day_combo_box.addItems(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        self.day_combo_box.currentIndexChanged.connect(self.update_table)
        self.day_combo_box.setStyleSheet("font-size: 16px;")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.checkbox_widget = QWidget()
        self.scroll_area.setWidget(self.checkbox_widget)
        self.checkbox_layout = QFormLayout(self.checkbox_widget)

        self.process_button = QPushButton('Process Substitutions')
        self.process_button.clicked.connect(self.process_substitutions)
        self.process_button.setStyleSheet("""
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

        self.save_pdf_button = QPushButton('Save as PDF')
        self.save_pdf_button.clicked.connect(self.save_timetable_as_pdf)
        self.save_pdf_button.setStyleSheet("""
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

        self.open_schedule_manager_button = QPushButton('Open Schedule Manager')
        self.open_schedule_manager_button.clicked.connect(self.open_schedule_manager)
        self.open_schedule_manager_button.setStyleSheet("""
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

        self.open_teacher_manager_button = QPushButton('Open Teacher Manager')
        self.open_teacher_manager_button.clicked.connect(self.open_teacher_manager)
        self.open_teacher_manager_button.setStyleSheet("""
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

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Day', 'Teacher', 'Period 1', 'Period 2', 'Period 3', 'Period 4',
            'Period 5', 'Period 6', 'Period 7', 'Period 8'
        ])

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #e0f2f1;
                gridline-color: #004d40;
            }
            QHeaderView::section {
                background-color: #004d40;
                color: #ffffff;
                font-size: 16px;
            }
            QTableWidget::item {
                padding: 10px;
                border: 1px solid #004d40;
                font-size: 14px;
            }
        """)
        self.table.setFont(QFont('Arial', 12))

        main_layout.addWidget(self.day_combo_box)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.process_button)
        main_layout.addWidget(self.save_pdf_button)
        main_layout.addWidget(self.open_schedule_manager_button)
        main_layout.addWidget(self.open_teacher_manager_button)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        self.update_table()

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 seconds)

    def load_absentees(self):
        if not os.path.exists('new_timetable.db'):
            QMessageBox.critical(self, 'Error', 'Database file not found!')
            return

        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()
        c.execute('SELECT DISTINCT teacher FROM timetable')
        rows = c.fetchall()
        conn.close()

        checked_states = {teacher: checkbox.isChecked() for teacher, checkbox in self.checkboxes.items() if checkbox}

        for i in reversed(range(self.checkbox_layout.count())):
            widget = self.checkbox_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.checkboxes = {}
        for row in rows:
            teacher_name = row[0]
            checkbox = QCheckBox(teacher_name)
            checkbox.setStyleSheet("font-size: 16px;")
            self.checkbox_layout.addWidget(checkbox)
            self.checkboxes[teacher_name] = checkbox

        for teacher, is_checked in checked_states.items():
            if teacher in self.checkboxes:
                self.checkboxes[teacher].setChecked(is_checked)

    def update_table(self):
        day = self.day_combo_box.currentText()
        self.load_absentees()
        if not os.path.exists('new_timetable.db'):
            QMessageBox.critical(self, 'Error', 'Database file not found!')
            return

        conn = sqlite3.connect('new_timetable.db')
        c = conn.cursor()
        c.execute('SELECT * FROM timetable WHERE day = ?', (day,))
        rows = c.fetchall()
        self.table.setRowCount(len(rows))
        for row_num, row_data in enumerate(rows):
            for col_num, col_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
        conn.close()

    def process_substitutions(self):
        print("Process button clicked")
        day = self.day_combo_box.currentText()
        absentees = [teacher for teacher, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        print(f"Selected absentees: {absentees}")

        if not absentees:
            QMessageBox.warning(self, 'Error', 'Please select at least one absentee')
            return

        updated_tt = self.create_time_table(day, absentees)
        print("Updated timetable:", updated_tt)

        self.display_updated_timetable(updated_tt)

    def create_time_table(self, day, absentees):
        if not os.path.exists('new_timetable.db'):
            QMessageBox.critical(self, 'Error', 'Database file not found!')
            return {}

        try:
            conn = sqlite3.connect('new_timetable.db')
            c = conn.cursor()

            c.execute('SELECT * FROM timetable WHERE day = ?', (day,))
            rows = c.fetchall()
            timetable = {}
            for row in rows:
                timetable[row[2]] = row[3:]

            presentees = {teacher for teacher in timetable if teacher not in absentees}

            periods = {i: [] for i in range(8)}
            for teacher in presentees:
                for i, period in enumerate(timetable[teacher]):
                    if period.upper() == 'FREE':
                        periods[i].append(teacher)

            for teacher in absentees:
                if teacher in timetable:
                    for i, period in enumerate(timetable[teacher]):
                        if period.upper() != 'FREE' and periods[i]:
                            replacement_teacher = random.choice(periods[i])
                            timetable[replacement_teacher] = (
                                timetable[replacement_teacher][:i] + (period,) + timetable[replacement_teacher][i + 1:]
                            )
                    del timetable[teacher]

            conn.close()
            return timetable
        except Exception as e:
            print(f"An error occurred in create_time_table: {e}")
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')
            return {}

    def display_updated_timetable(self, updated_tt):
        self.table.setRowCount(len(updated_tt))
        row_num = 0
        for teacher, periods in updated_tt.items():
            row_data = [row_num + 1, self.day_combo_box.currentText(), teacher] + list(periods)
            for col_num, col_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
            row_num += 1

    def save_timetable_as_pdf(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, 'Save PDF', '', 'PDF Files (*.pdf)')
            if file_name:
                doc = SimpleDocTemplate(file_name, pagesize=letter)
                elements = []

                stylesheet = getSampleStyleSheet()

                # Add absentee names at the top
                absentee_names = [teacher for teacher, checkbox in self.checkboxes.items() if checkbox.isChecked()]
                absentee_text = 'Absentees: ' + ', '.join(absentee_names) if absentee_names else 'No absentees'
                absentee_paragraph = Paragraph(absentee_text, stylesheet['Normal'])
                elements.append(absentee_paragraph)
                elements.append(Spacer(1, 12))

                # Change title
                title = Paragraph('Today\'s Timetable', stylesheet['Title'])
                elements.append(title)
                elements.append(Spacer(1, 12))

                # Add table
                table_data = []
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                table_data.append(headers)
                for row in range(self.table.rowCount()):
                    row_data = [self.table.item(row, col).text() if self.table.item(row, col) else '' for col in
                                range(self.table.columnCount())]
                    table_data.append(row_data)

                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
                doc.build(elements)
                QMessageBox.information(self, 'Success', 'PDF saved successfully!')
        except Exception as e:
            print(f"An error occurred while saving the PDF: {e}")
            QMessageBox.critical(self, 'Error', f'An error occurred while saving the PDF: {e}')

    def open_schedule_manager(self):
        if self.schedule_manager is None:
            self.schedule_manager = ScheduleManager()
        self.schedule_manager.show()

    def open_teacher_manager(self):
        if self.teacher_manager is None:
            self.teacher_manager = TeacherManager()
        self.teacher_manager.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = TimeTableManager()
    main_win.show()
    sys.exit(app.exec_())
