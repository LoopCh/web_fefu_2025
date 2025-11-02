from django.core.management.base import BaseCommand
from django.utils import timezone
from fefu_lab.models import Student, Instructor, Course, Enrollment
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'
    
    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')
        
        self.stdout.write('Удаление старых данных...')
        Enrollment.objects.all().delete()
        Course.objects.all().delete()
        Student.objects.all().delete()
        Instructor.objects.all().delete()
        
        self.stdout.write('Создание преподавателей...')
        instructors = [
            Instructor(
                first_name='Иван',
                last_name='Петров',
                email='i.petrov@dvfu.ru',
                specialization='Кибербезопасность',
                degree='PHD',
                bio='Кандидат технических наук, специалист по защите информации'
            ),
            Instructor(
                first_name='Мария',
                last_name='Сидорова',
                email='m.sidorova@dvfu.ru',
                specialization='Веб-разработка',
                degree='DSC',
                bio='Доктор технических наук, эксперт в области веб-технологий'
            ),
            Instructor(
                first_name='Алексей',
                last_name='Козлов',
                email='a.kozlov@dvfu.ru',
                specialization='Сетевые технологии',
                degree='PHD',
                bio='Кандидат наук, специалист по компьютерным сетям'
            ),
        ]
        
        for instructor in instructors:
            instructor.save()
        
        self.stdout.write('Создание студентов...')
        students = [
            Student(
                first_name='Анна',
                last_name='Иванова',
                email='anna.ivanova@students.dvfu.ru',
                birth_date=date(2003, 5, 15),
                faculty='CS'
            ),
            Student(
                first_name='Дмитрий',
                last_name='Смирнов',
                email='dmitry.smirnov@students.dvfu.ru',
                birth_date=date(2002, 8, 22),
                faculty='SE'
            ),
            Student(
                first_name='Екатерина',
                last_name='Попова',
                email='ekaterina.popova@students.dvfu.ru',
                birth_date=date(2003, 3, 10),
                faculty='IT'
            ),
            Student(
                first_name='Михаил',
                last_name='Васильев',
                email='mikhail.vasilyev@students.dvfu.ru',
                birth_date=date(2003, 11, 5),
                faculty='DS'
            ),
            Student(
                first_name='Ольга',
                last_name='Новикова',
                email='olga.novikova@students.dvfu.ru',
                birth_date=date(2002, 12, 30),
                faculty='WEB'
            ),
            Student(
                first_name='Сергей',
                last_name='Петров',
                email='sergey.petrov@students.dvfu.ru',
                birth_date=date(2003, 7, 18),
                faculty='CS'
            ),
        ]
        
        for student in students:
            student.save()
        
        self.stdout.write('Создание курсов...')
        courses = [
            Course(
                title='Основы Python',
                slug='python-basics',
                description='Базовый курс по программированию на языке Python. Изучение синтаксиса, структур данных и основ объектно-ориентированного программирования.',
                duration=36,
                instructor=instructors[0],
                level='BEGINNER',
                max_students=25,
                price=0
            ),
            Course(
                title='Веб-безопасность',
                slug='web-security',
                description='Продвинутый курс по защите веб-приложений. SQL-инъекции, XSS, CSRF и другие уязвимости. Практические методы защиты.',
                duration=48,
                instructor=instructors[0],
                level='ADVANCED',
                max_students=20,
                price=15000
            ),
            Course(
                title='Современный JavaScript',
                slug='modern-javascript',
                description='Изучение современных возможностей JavaScript: ES6+, асинхронное программирование, работа с фреймворками React и Vue.',
                duration=42,
                instructor=instructors[1],
                level='INTERMEDIATE',
                max_students=30,
                price=12000
            ),
            Course(
                title='Защита сетей',
                slug='network-defense',
                description='Курс по защите компьютерных сетей. Firewalls, IDS/IPS, VPN и методы атак на сети. Практика на реальных примерах.',
                duration=40,
                instructor=instructors[2],
                level='ADVANCED',
                max_students=15,
                price=18000
            ),
            Course(
                title='Django для начинающих',
                slug='django-beginners',
                description='Введение в веб-разработку на Python с использованием фреймворка Django. Создание полноценных веб-приложений.',
                duration=50,
                instructor=instructors[1],
                level='BEGINNER',
                max_students=20,
                price=10000
            ),
        ]
        
        for course in courses:
            course.save()
        
        self.stdout.write('Создание записей на курсы...')
        enrollments = [
            Enrollment(student=students[0], course=courses[0], status='ACTIVE'),
            Enrollment(student=students[0], course=courses[1], status='ACTIVE'),
            Enrollment(student=students[1], course=courses[0], status='ACTIVE'),
            Enrollment(student=students[1], course=courses[2], status='ACTIVE'),
            Enrollment(student=students[2], course=courses[0], status='COMPLETED'),
            Enrollment(student=students[2], course=courses[4], status='ACTIVE'),
            Enrollment(student=students[3], course=courses[3], status='ACTIVE'),
            Enrollment(student=students[4], course=courses[2], status='ACTIVE'),
            Enrollment(student=students[4], course=courses[4], status='ACTIVE'),
            Enrollment(student=students[5], course=courses[1], status='ACTIVE'),
        ]
        
        for enrollment in enrollments:
            enrollment.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nУспешно создано:\n'
                f'  • {len(instructors)} преподавателей\n'
                f'  • {len(students)} студентов\n'
                f'  • {len(courses)} курсов\n'
                f'  • {len(enrollments)} записей на курсы'
            )
        )
