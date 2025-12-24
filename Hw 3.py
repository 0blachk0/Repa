import sqlite3
from typing import List, Tuple, Optional, Any


class UniversityDatabase:
    def __init__(self, db_name: str = 'university.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()

        self._is_database_populated = self._check_database_populated()

    def _connect(self) -> None:
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            print(f"Подключение к бд '{self.db_name}' установлено")
        except sqlite3.Error as e:
            print(f"Ошибка подключения к бд: {e}")
            raise

    def _check_database_populated(self) -> bool:
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Students")
            students_count = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM Courses")
            courses_count = self.cursor.fetchone()[0]

            return students_count > 0 and courses_count > 0
        except sqlite3.OperationalError:
            return False

    def create_tables(self) -> None:
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                age INTEGER CHECK(age >= 0 AND age <= 150),
                city TEXT NOT NULL
            )
            ''')

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                time_start TEXT NOT NULL,
                time_end TEXT NOT NULL,
                CHECK(time_end > time_start)
            )
            ''')

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Student_courses (
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES Courses(id) ON DELETE CASCADE
            )
            ''')

            self.conn.commit()
            print("Таблицы успешно созданы или уже существуют")
        except sqlite3.Error as e:
            print(f"Ошибка: {e}")
            raise

    def populate_database(self) -> None:
        if self._is_database_populated:
            print("База данных уже заполнена")
            return

        print("Начинается заполнение")

        try:
            self.cursor.execute("DELETE FROM Student_courses")
            self.cursor.execute("DELETE FROM Students")
            self.cursor.execute("DELETE FROM Courses")

            self.cursor.execute("DELETE FROM sqlite_sequence")

            courses = [
                (1, 'python', '21.07.21', '21.08.21'),
                (2, 'java', '13.07.21', '16.08.21')
            ]

            self.cursor.executemany('''
            INSERT INTO Courses (id, name, time_start, time_end) 
            VALUES (?, ?, ?, ?)
            ''', courses)

            students = [
                (1, 'Max', 'Brooks', 24, 'Spb'),
                (2, 'John', 'Stones', 15, 'Spb'),
                (3, 'Andy', 'Wings', 45, 'Manchester'),
                (4, 'Kate', 'Brooks', 34, 'Spb')
            ]

            self.cursor.executemany('''
            INSERT INTO Students (id, name, surname, age, city) 
            VALUES (?, ?, ?, ?, ?)
            ''', students)

            student_courses = [
                (1, 1),
                (2, 1),
                (3, 1),
                (4, 2)
            ]

            self.cursor.executemany('''
            INSERT INTO Student_courses (student_id, course_id) 
            VALUES (?, ?)
            ''', student_courses)

            self.conn.commit()
            self._is_database_populated = True
            print("База данных заполнена")

        except sqlite3.Error as e:
            print(f"Ошибка при заполнении бд: {e}")
            self.conn.rollback()
            raise

    def execute_query(self, query: str, params: Tuple = (), fetch_all: bool = True) -> Optional[List[Tuple]]:
        try:
            self.cursor.execute(query, params)

            if query.strip().upper().startswith(('SELECT', 'PRAGMA', 'EXPLAIN')):
                if fetch_all:
                    return self.cursor.fetchall()
                else:
                    return self.cursor.fetchone()
            else:
                self.conn.commit()
                return None

        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            print(f"Запрос: {query}")
            print(f"Параметры: {params}")
            return None

    def get_students_over_age(self, min_age: int = 30) -> List[Tuple]:
        query = '''
        SELECT id, name, surname, age, city 
        FROM Students 
        WHERE age > ?
        ORDER BY age DESC
        '''
        return self.execute_query(query, (min_age,), fetch_all=True) or []

    def get_students_by_course(self, course_name: str) -> List[Tuple]:
        query = '''
        SELECT s.id, s.name, s.surname, s.age, s.city
        FROM Students s
        JOIN Student_courses sc ON s.id = sc.student_id
        JOIN Courses c ON sc.course_id = c.id
        WHERE c.name = ?
        ORDER BY s.surname
        '''
        return self.execute_query(query, (course_name,), fetch_all=True) or []

    def get_students_by_course_and_city(self, course_name: str, city: str) -> List[Tuple]:
        query = '''
        SELECT s.id, s.name, s.surname, s.age, s.city
        FROM Students s
        JOIN Student_courses sc ON s.id = sc.student_id
        JOIN Courses c ON sc.course_id = c.id
        WHERE c.name = ? AND s.city = ?
        ORDER BY s.age
        '''
        return self.execute_query(query, (course_name, city), fetch_all=True) or []

    def add_student(self, name: str, surname: str, age: int, city: str) -> Optional[int]:
        query = '''
        INSERT INTO Students (name, surname, age, city)
        VALUES (?, ?, ?, ?)
        '''

        try:
            self.cursor.execute(query, (name, surname, age, city))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении студента: {e}")
            return None

    def get_all_students(self) -> List[Tuple]:
        return self.execute_query("SELECT * FROM Students ORDER BY id", fetch_all=True) or []

    def get_all_courses(self) -> List[Tuple]:
        return self.execute_query("SELECT * FROM Courses ORDER BY id", fetch_all=True) or []

    def get_student_courses(self) -> List[Tuple]:
        return self.execute_query("SELECT * FROM Student_courses ORDER BY student_id", fetch_all=True) or []

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            print("Соединение с бд закрыто")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def run_tests() -> None:


    print("Тесты:")

    db = UniversityDatabase('test_university.db')

    try:
        db.create_tables()

        db.populate_database()

        print("\n1. Тест заполнения бд:")
        students = db.get_all_students()
        courses = db.get_all_courses()
        student_courses = db.get_student_courses()

        print(f"   Студентов в базе: {len(students)}")
        print(f"   Курсов в базе: {len(courses)}")
        print(f"   Записей о курсах студентов: {len(student_courses)}")

        print("\n2. Тест: студенты старше 30 лет:")
        students_over_30 = db.get_students_over_age(30)
        print(f"   Найдено студентов старше 30 лет: {len(students_over_30)}")
        for student in students_over_30:
            print(f"   - {student[1]} {student[2]}, {student[3]} лет, {student[4]}")

        print("\n3. Тест: студенты на курсе Python:")
        python_students = db.get_students_by_course('python')
        print(f"   Найдено студентов на курсе Python: {len(python_students)}")
        for student in python_students:
            print(f"   - {student[1]} {student[2]}, {student[3]} лет, {student[4]}")

        print("\n4. Тест: студенты из Spb на курсе Python:")
        python_spb_students = db.get_students_by_course_and_city('python', 'Spb')
        print(f"   Найдено студентов из Spb на курсе Python: {len(python_spb_students)}")
        for student in python_spb_students:
            print(f"   - {student[1]} {student[2]}, {student[3]} лет")

        print("\n5. Тест: добавление нового студента:")
        new_student_id = db.add_student('Илья', 'Максимов', 25, 'Moscow')
        if new_student_id:
            print(f"   Новый студент добавлен с ID: {new_student_id}")

            all_students = db.get_all_students()
            print(f"   Всего студентов после добавления: {len(all_students)}")

        print("\n6. Тест: универсальный метод execute_query:")

        custom_query = """
        SELECT s.name, s.surname, c.name as course_name
        FROM Students s
        JOIN Student_courses sc ON s.id = sc.student_id
        JOIN Courses c ON sc.course_id = c.id
        ORDER BY s.surname
        """
        result = db.execute_query(custom_query)
        print(f"   Результат произвольного запроса: {len(result)} записей")

        stats_query = """
        SELECT 
            COUNT(DISTINCT s.id) as total_students,
            COUNT(DISTINCT c.id) as total_courses,
            AVG(s.age) as avg_age
        FROM Students s
        LEFT JOIN Student_courses sc ON s.id = sc.student_id
        LEFT JOIN Courses c ON sc.course_id = c.id
        """
        stats = db.execute_query(stats_query, fetch_all=False)
        if stats:
            print(f"   Статистика: {stats[0]} студентов, {stats[1]} курсов, средний возраст: {stats[2]:.1f} лет")

        print("\n7. Тест: защита от повторного заполнения:")
        db.populate_database()

        print("\n")
        print("Тесты пройдены")

    except Exception as e:
        print(f"\nОшибка при тестировании: {e}")
        raise
    finally:
        db.close()

def main() -> None:
    print("Программа управления базой данных")

    with UniversityDatabase() as db:
        db.create_tables()

        db.populate_database()

        print("\n")
        print("Анализ данных")

        print("\n1. Студенты старше 30 лет:")
        students = db.get_students_over_age(30)
        if students:
            for student in students:
                print(f"   {student[1]} {student[2]} - {student[3]} лет, {student[4]}")
        else:
            print("   Нет студентов старше 30 лет")

        print("\n2. Студенты на курсе Python:")
        python_students = db.get_students_by_course('python')
        if python_students:
            for student in python_students:
                print(f"   {student[1]} {student[2]} - {student[3]} лет, {student[4]}")
        else:
            print("   На курсе Python нет студентов")

        print("\n3. Студенты из Spb на курсе Python:")
        spb_python_students = db.get_students_by_course_and_city('python', 'Spb')
        if spb_python_students:
            for student in spb_python_students:
                print(f"   {student[1]} {student[2]} - {student[3]} лет")
        else:
            print("   Нет студентов из Spb на курсе Python")

        print("\n4. Произвольный запрос: студенты и их курсы")
        query = """
        SELECT s.name || ' ' || s.surname as student_name,
               c.name as course_name,
               c.time_start || ' - ' || c.time_end as course_period
        FROM Students s
        JOIN Student_courses sc ON s.id = sc.student_id
        JOIN Courses c ON sc.course_id = c.id
        ORDER BY s.surname, c.name
        """

        results = db.execute_query(query)
        if results:
            for row in results:
                print(f"   {row[0]} → {row[1]} ({row[2]})")

    print("\n")
    print("Работа завершена")

if __name__ == "__main__":
    run_tests()

    print("\n")

    main()