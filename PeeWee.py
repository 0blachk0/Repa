from peewee import *
from typing import List, Optional, Dict, Any
from datetime import date
import os

database = SqliteDatabase('university_peewee.db')


class BaseModel(Model):

    class Meta:
        database = database

class Student(BaseModel):
    id = AutoField()
    name = CharField(max_length=50)
    surname = CharField(max_length=50)
    age = IntegerField()
    city = CharField(max_length=50)

    class Meta:
        table_name = 'students'

    def __str__(self):
        return f"{self.name} {self.surname}, {self.age} лет, {self.city}"


class Course(BaseModel):
    id = AutoField()
    name = CharField(max_length=50)
    time_start = CharField(max_length=10)
    time_end = CharField(max_length=10)

    class Meta:
        table_name = 'courses'

    def __str__(self):
        return f"{self.name} ({self.time_start} - {self.time_end})"


class StudentCourse(BaseModel):
    student = ForeignKeyField(Student, backref='courses', on_delete='CASCADE')
    course = ForeignKeyField(Course, backref='students', on_delete='CASCADE')

    class Meta:
        table_name = 'student_courses'
        primary_key = CompositeKey('student', 'course')


class UniversityDatabase:
    def __init__(self, db_path: str = 'university_peewee.db'):
        self.db_path = db_path
        self.database = SqliteDatabase(db_path)

        self._connect_database()

    def _connect_database(self) -> None:
        self.database.bind([Student, Course, StudentCourse])

    def create_tables(self) -> None:
        try:
            self.database.connect()
            self.database.create_tables([Student, Course, StudentCourse])
            print("Таблицы успешно созданы")
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            self.database.close()

    def is_database_populated(self) -> bool:
        try:
            self.database.connect()
            return Student.select().count() > 0 and Course.select().count() > 0
        finally:
            self.database.close()

    def populate_database(self) -> None:
        if self.is_database_populated():
            print("База данных уже заполнена. Пропускаем заполнение.")
            return

        print("Заполнение базы данных данными")

        try:
            self.database.connect()

            with self.database.atomic():
                StudentCourse.delete().execute()
                Student.delete().execute()
                Course.delete().execute()

                courses_data = [
                    {'name': 'python', 'time_start': '21.07.21', 'time_end': '21.08.21'},
                    {'name': 'java', 'time_start': '13.07.21', 'time_end': '16.08.21'}
                ]

                created_courses = {}
                for course_data in courses_data:
                    course = Course.create(**course_data)
                    created_courses[course_data['name']] = course

                students_data = [
                    {'name': 'Max', 'surname': 'Brooks', 'age': 24, 'city': 'Spb'},
                    {'name': 'John', 'surname': 'Stones', 'age': 15, 'city': 'Spb'},
                    {'name': 'Andy', 'surname': 'Wings', 'age': 45, 'city': 'Manchester'},
                    {'name': 'Kate', 'surname': 'Brooks', 'age': 34, 'city': 'Spb'}
                ]

                created_students = []
                for student_data in students_data:
                    student = Student.create(**student_data)
                    created_students.append(student)

                student_courses_data = [
                    (created_students[0], created_courses['python']),
                    (created_students[1], created_courses['python']),
                    (created_students[2], created_courses['python']),
                    (created_students[3], created_courses['java'])
                ]

                for student, course in student_courses_data:
                    StudentCourse.create(student=student, course=course)

            print("База данных успешно заполнена!")

        except Exception as e:
            print(f"Ошибка при заполнении базы данных: {e}")
            raise
        finally:
            self.database.close()

    def get_all_students(self) -> List[Student]:
        try:
            self.database.connect()
            return list(Student.select().order_by(Student.surname, Student.name))
        finally:
            self.database.close()

    def get_all_courses(self) -> List[Course]:
        try:
            self.database.connect()
            return list(Course.select().order_by(Course.name))
        finally:
            self.database.close()

    def get_students_over_age(self, min_age: int = 30) -> List[Student]:
        try:
            self.database.connect()
            query = Student.select().where(Student.age > min_age).order_by(Student.age.desc())
            return list(query)
        finally:
            self.database.close()

    def get_students_by_course(self, course_name: str) -> List[Student]:
        try:
            self.database.connect()
            query = (Student
                     .select()
                     .join(StudentCourse)
                     .join(Course)
                     .where(Course.name == course_name)
                     .order_by(Student.surname, Student.name))
            return list(query)
        finally:
            self.database.close()

    def get_students_by_course_and_city(self, course_name: str, city: str) -> List[Student]:
        try:
            self.database.connect()
            query = (Student
                     .select()
                     .join(StudentCourse)
                     .join(Course)
                     .where((Course.name == course_name) & (Student.city == city))
                     .order_by(Student.surname, Student.name))
            return list(query)
        finally:
            self.database.close()

    def add_student(self, name: str, surname: str, age: int, city: str) -> Optional[Student]:
        try:
            self.database.connect()
            student = Student.create(name=name, surname=surname, age=age, city=city)
            return student
        except Exception as e:
            print(f"Ошибка при добавлении студента: {e}")
            return None
        finally:
            self.database.close()

    def add_course(self, name: str, time_start: str, time_end: str) -> Optional[Course]:
        try:
            self.database.connect()
            course = Course.create(name=name, time_start=time_start, time_end=time_end)
            return course
        except Exception as e:
            print(f"Ошибка при добавлении курса: {e}")
            return None
        finally:
            self.database.close()

    def enroll_student_to_course(self, student_id: int, course_id: int) -> bool:
        try:
            self.database.connect()
            StudentCourse.create(student=student_id, course=course_id)
            return True
        except Exception as e:
            print(f"Ошибка при записи на курс: {e}")
            return False
        finally:
            self.database.close()

    def get_student_courses(self, student_id: int) -> List[Course]:
        try:
            self.database.connect()
            query = (Course
                     .select()
                     .join(StudentCourse)
                     .join(Student)
                     .where(Student.id == student_id))
            return list(query)
        finally:
            self.database.close()

    def get_course_students(self, course_id: int) -> List[Student]:
        try:
            self.database.connect()
            query = (Student
                     .select()
                     .join(StudentCourse)
                     .join(Course)
                     .where(Course.id == course_id))
            return list(query)
        finally:
            self.database.close()

    def delete_student(self, student_id: int) -> bool:
        try:
            self.database.connect()
            student = Student.get(Student.id == student_id)
            student.delete_instance()
            return True
        except Student.DoesNotExist:
            print(f"Студент с ID {student_id} не найден")
            return False
        except Exception as e:
            print(f"Ошибка при удалении студента: {e}")
            return False
        finally:
            self.database.close()

    def execute_custom_query(self, query: str) -> List[Dict[str, Any]]:
        try:
            self.database.connect()
            cursor = self.database.execute_sql(query)

            columns = [desc[0] for desc in cursor.description]

            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []
        finally:
            self.database.close()

    def close(self) -> None:
        if not self.database.is_closed():
            self.database.close()


def run_tests() -> None:
    print("Тесты")

    test_db_path = 'test_university_peewee.db'
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = UniversityDatabase(test_db_path)

    try:
        print("\n1. Тест: создание таблиц")
        db.create_tables()
        print("   Таблицы созданы")

        print("\n2. Тест: заполнение базы данных")
        db.populate_database()

        students = db.get_all_students()
        courses = db.get_all_courses()
        print(f"   Студентов добавлено: {len(students)}")
        print(f"   Курсов добавлено: {len(courses)}")

        print("\n3. Тест: студенты старше 30 лет")
        students_over_30 = db.get_students_over_age(30)
        print(f"   Найдено студентов: {len(students_over_30)}")
        assert len(students_over_30) == 2, f"Ожидалось 2, получили {len(students_over_30)}"
        for student in students_over_30:
            print(f"   - {student.name} {student.surname}, {student.age} лет")
        print("   Тест пройден")

        print("\n4. Тест: студенты на курсе Python")
        python_students = db.get_students_by_course('python')
        print(f"   Найдено студентов: {len(python_students)}")
        assert len(python_students) == 3, f"Ожидалось 3, получили {len(python_students)}"
        for student in python_students:
            print(f"   - {student.name} {student.surname}")
        print("   Тест пройден")

        print("\n5. Тест: студенты из Spb на курсе Python")
        spb_python_students = db.get_students_by_course_and_city('python', 'Spb')
        print(f"   Найдено студентов: {len(spb_python_students)}")
        assert len(spb_python_students) == 2, f"Ожидалось 2, получили {len(spb_python_students)}"
        for student in spb_python_students:
            print(f"   - {student.name} {student.surname}")
        print("   Тест пройден")

        print("\n6. Тест: добавление нового студента")
        new_student = db.add_student('Илья', 'Максимов', 25, 'Moscow')
        assert new_student is not None, "Студент не был добавлен"
        print(f"   Добавлен студент: {new_student.name} {new_student.surname}")

        print("\n7. Тест: запись студента на курс")
        all_courses = db.get_all_courses()
        java_course = next((c for c in all_courses if c.name == 'java'), None)

        if java_course and new_student:
            success = db.enroll_student_to_course(new_student.id, java_course.id)
            assert success, "Не удалось записать студента на курс"

            student_courses = db.get_student_courses(new_student.id)
            assert len(student_courses) == 1, "Студент должен быть на одном курсе"
            assert student_courses[0].name == 'java', "Студент должен быть на курсе Java"
            print(f"   Студент записан на курс: {student_courses[0].name}")

        print("\n8. Тест: произвольный SQL запрос")
        query = """
        SELECT s.name, s.surname, c.name as course_name
        FROM students s
        JOIN student_courses sc ON s.id = sc.student_id
        JOIN courses c ON sc.course_id = c.id
        ORDER BY s.surname
        """
        results = db.execute_custom_query(query)
        print(f"   Получено записей: {len(results)}")
        assert len(results) > 0, "Запрос должен вернуть результаты"
        print("   Тест пройден")

        print("\n9. Тест: защита от повторного заполнения")
        db.populate_database()

        print("\n")
        print("Все тесты пройдены")

    except AssertionError as e:
        print(f"\n Ошибка теста: {e}")
        raise
    except Exception as e:
        print(f"\n Непредвиденная ошибка: {e}")
        raise
    finally:
        db.close()


def main() -> None:

    print("Программа управления базой данных")

    db = UniversityDatabase()

    try:
        db.create_tables()

        db.populate_database()

        print("\n")
        print("Анализ данных")

        print("\n1. Студенты старше 30 лет:")
        students_over_30 = db.get_students_over_age(30)
        if students_over_30:
            for student in students_over_30:
                print(f"   {student.name} {student.surname} - {student.age} лет, {student.city}")
        else:
            print("   Нет студентов старше 30 лет")

        print("\n2. Студенты на курсе Python:")
        python_students = db.get_students_by_course('python')
        if python_students:
            for student in python_students:
                print(f"   {student.name} {student.surname} - {student.age} лет, {student.city}")
        else:
            print("   На курсе Python нет студентов")

        print("\n3. Студенты из Spb на курсе Python:")
        spb_python_students = db.get_students_by_course_and_city('python', 'Spb')
        if spb_python_students:
            for student in spb_python_students:
                print(f"   {student.name} {student.surname} - {student.age} лет")
        else:
            print("   Нет студентов из Spb на курсе Python")

        print("\n4. Общая статистика:")
        all_students = db.get_all_students()
        all_courses = db.get_all_courses()

        stats_query = """
        SELECT 
            COUNT(DISTINCT s.id) as total_students,
            COUNT(DISTINCT c.id) as total_courses,
            AVG(s.age) as avg_age,
            COUNT(DISTINCT sc.student_id) as students_with_courses
        FROM students s
        LEFT JOIN student_courses sc ON s.id = sc.student_id
        LEFT JOIN courses c ON sc.course_id = c.id
        """

        stats = db.execute_custom_query(stats_query)
        if stats:
            stat = stats[0]
            print(f"   Всего студентов: {stat['total_students']}")
            print(f"   Всего курсов: {stat['total_courses']}")
            print(f"   Средний возраст: {stat['avg_age']:.1f} лет")
            print(f"   Студентов с курсами: {stat['students_with_courses']}")

        print("\n5. Добавление нового студента:")
        new_student = db.add_student('Анна', 'Смирнова', 28, 'Москва')
        if new_student:
            print(f"   Добавлен: {new_student.name} {new_student.surname}")

            python_course = next((c for c in all_courses if c.name == 'python'), None)
            if python_course:
                db.enroll_student_to_course(new_student.id, python_course.id)
                print(f"   Записана на курс: {python_course.name}")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        db.close()

    print("\n")
    print("Программа завершена")

if __name__ == "__main__":
    run_tests()

    print("\n")
    print("Основная программа")

    main()