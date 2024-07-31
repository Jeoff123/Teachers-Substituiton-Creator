import sqlite3
import random

def create_time_table(day, absentees):
    conn = sqlite3.connect('timetable.db')
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
                        timetable[replacement_teacher][:i] + (period,) + timetable[replacement_teacher][i+1:]
                    )

            # Remove absent teacher's record
            del timetable[teacher]

    conn.close()
    return timetable

if __name__ == '__main__':
    # Test the function with a day and a list of absentees
    day = 'Monday'
    absentees = ['T1']
    updated_tt = create_time_table(day, absentees)
    print(updated_tt)
