from django.shortcuts import render
from django.http import HttpResponse

STUDENTS_DATA = {
    1: {
        'info': 'Иван Петров',
        'faculty': 'Кибербезопасность',
        'status': 'Активный',
        'year': 3
    },
    2: {
        'info': 'Мария Сидорова', 
        'faculty': 'Информатика',
        'status': 'Активный',
        'year': 2
    },
    3: {
        'info': 'Алексей Козлов',
        'faculty': 'Программная инженерия', 
        'status': 'Выпускник',
        'year': 5
    }
}

COURSES_DATA = {
    'python-basics': {
        'name': 'Основы программирования на Python',
        'duration': 36,
        'description': 'Базовый курс по программированию на языке Python для начинающих.',
        'instructor': 'Доцент Петров И.С.',
        'level': 'Начальный'
    },
    'web-security': {
        'name': 'Веб-безопасность',
        'duration': 48,
        'description': 'Курс по защите веб-приложений от современных угроз.',
        'instructor': 'Профессор Сидоров А.В.',
        'level': 'Продвинутый'
    },
    'network-defense': {
        'name': 'Защита сетей',
        'duration': 42,
        'description': 'Изучение методов и технологий защиты компьютерных сетей.',
        'instructor': 'Доцент Козлова М.П.',
        'level': 'Средний'
    }
}

# Create your views here.
def home(request):
    ctx = {"title": "Главная", "user": None}
    return render(request, "fefu_lab/home.html", ctx)

def about(request):
    return render(request, "fefu_lab/about.html", {"title": "О нас"})

def student_detail(request, student_id):
    if student_id in STUDENTS_DATA:
        student_data = STUDENTS_DATA[student_id]
        return render(request, 'fefu_lab/student_detail.html', {
            'students': STUDENTS_DATA,
            'student_id': student_id,
            'student_info': student_data['info'],
            'faculty': student_data['faculty'],
            'status': student_data['status'],
            'year': student_data['year']
        })
    else:
        return page_not_found(request, "Студент с таким ID не найден")

def course_detail(request, course_slug):
    if course_slug in COURSES_DATA:
        course_data = COURSES_DATA[course_slug]
        return render(request, 'fefu_lab/course_detail.html', {
            'courses': COURSES_DATA,
            'description': course_data['description'],
            'course_slug': course_slug,
            'name': course_data['name'],
            'duration': course_data['duration'],
            'instructor': course_data['instructor'],
            'level': course_data['level']
        })
    else:
        return page_not_found(request, "Курс с таким именем не найден")


def feedback(request):
    return HttpResponse('Ok')

def page_not_found(request, exception):
    return render(request, '404.html', status=404)