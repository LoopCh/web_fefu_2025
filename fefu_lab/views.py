from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .forms import FeedbackForm, RegistrationForm, LogonForm
from .models import UserProfile
from django.views.decorators.csrf import csrf_protect

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
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():  # Django запустит clean_<field> и clean()
            return render(request, 'fefu_lab/success.html', {
                'title': 'Сообщение отправлено',
                'message': 'Спасибо за обратную связь!'
            })
    else:
        form = FeedbackForm()
    return render(request, 'fefu_lab/feedback.html', {
        'form': form,
        'title': 'Обратная связь'
    })

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            UserProfile.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'] 
            )
            return render(request, 'fefu_lab/success.html', {
                'title': 'Регистрация',
                'message': 'Регистрация прошла успешно.'
            })
    else:
        form = RegistrationForm()
    return render(request, 'fefu_lab/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

@csrf_protect
def login(request):
    if request.method == 'POST':
        form = LogonForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            return render(request, 'fefu_lab/success.html', {
                'title': 'Вход',
                'message': 'Вход прошел успешно.'
            })
    else:
        form = LogonForm()
    return render(request, 'fefu_lab/login.html', {
        'form': form,
        'title': 'Вход'
    })


def page_not_found(request, exception):
    return render(request, '404.html', status=404)