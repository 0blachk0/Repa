import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute('''
CREATE TABLE IF NOT EXISTS Students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    age INTEGER NOT NULL,
    city TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    time_start TEXT NOT NULL,
    time_end TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Student_courses (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Courses(id) ON DELETE CASCADE
)
''')

print("Таблицы созданы")

cursor.execute("DELETE FROM Student_courses")
cursor.execute("DELETE FROM Students")
cursor.execute("DELETE FROM Courses")

cursor.executemany('''
INSERT INTO Courses (id, name, time_start, time_end) VALUES (?, ?, ?, ?)
''', [
    (1, 'python', '21.07.21', '21.08.21'),
    (2, 'java', '13.07.21', '16.08.21')
])

cursor.executemany('''
INSERT INTO Students (id, name, surname, age, city) VALUES (?, ?, ?, ?, ?)
''', [
    (1, 'Max', 'Brooks', 24, 'Spb'),
    (2, 'John', 'Stones', 15, 'Spb'),
    (3, 'Andy', 'Wings', 45, 'Manchester'),
    (4, 'Kate', 'Brooks', 34, 'Spb')
])

cursor.executemany('''
INSERT INTO Student_courses (student_id, course_id) VALUES (?, ?)
''', [
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 2)
])

conn.commit()
print("Данные добавлены")

print("1. Студенты старше 30 лет:")
cursor.execute("SELECT * FROM Students WHERE age > 30")
for row in cursor.fetchall():
    print(f"  {row[1]} {row[2]}, {row[3]} лет, {row[4]}")

print("\n2. Студенты, проходящие курс Python:")
cursor.execute('''
SELECT s.name, s.surname, s.age, s.city
FROM Students s
JOIN Student_courses sc ON s.id = sc.student_id
JOIN Courses c ON sc.course_id = c.id
WHERE c.name = 'python'
''')
for row in cursor.fetchall():
    print(f"  {row[0]} {row[1]}, {row[2]} лет, {row[3]}")

print("\n3. Студенты из Spb, проходящие курс Python:")
cursor.execute('''
SELECT s.name, s.surname, s.age
FROM Students s
JOIN Student_courses sc ON s.id = sc.student_id
JOIN Courses c ON sc.course_id = c.id
WHERE c.name = 'python' AND s.city = 'Spb'
''')
for row in cursor.fetchall():
    print(f"  {row[0]} {row[1]}, {row[2]} лет")

conn.close()
