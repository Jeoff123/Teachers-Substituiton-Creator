# Time Table Manager

**Teachers Substitution Creator** is a PyQt5-based application designed to manage teacher schedules and efficiently generate substitution timetables. This project aims to streamline handling teacher absences and ensure smooth school operations.

## Features

- **Teacher Manager**: Add, update, and delete teacher information.
- **Schedule Manager**: Manage and update teacher schedules.
- **Timetable Manager**: View and modify timetables, process substitutions, and generate updated timetables.
- **Dynamic Substitution**: Automatically generate substitution timetables based on absentees and available teachers.

## Getting Started

### Prerequisites

- Python 3.x
- PyQt5
- SQLite3
- Reportlab (for PDF generation)

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/Teachers-Substitution-Creator.git
    cd Teachers-Substitution-Creator
    ```

2. **Install the required packages:**
    ```sh
    pip install pyqt5 reportlab
    ```

3. **Set up the database:**
    ```sh
    python db_setup.py
    ```

### Usage

1. **Run the main application:**
    ```sh
    python main.py
    ```

2. **Use the interface to manage teacher information, schedules, and generate substitution timetables.**

### Files

- `main.py`: The main application file.
- `db_setup.py`: Script to set up the SQLite database.
- `algorithm.py`: Contains the substitution algorithm.
- `teacher_manager.py`: Manages teacher data.
- `schedule_manager.py`: Manages teacher schedules.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or issues, please contact Jeoff George Giby at [jeoff_george_giby](https://www.instagram.com/jeoff_george_giby/).

---

Enjoy using Teachers Substitution Creator!
