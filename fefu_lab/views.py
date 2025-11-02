from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect

from .forms import FeedbackForm, RegistrationForm, LogonForm, StudentRegistrationForm, EnrollmentForm
from .models import UserProfile, Student, Course, Instructor, Enrollment

def home(request):
    total_students = Student.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_instructors = Instructor.objects.filter(is_active=True).count()
    recent_courses = Course.objects.filter(is_active=True).select_related('instructor').order_by('-created_at')[:3]
    
    ctx = {
        "title": "Главная",
        "user": request.session.get('username'),
        "total_students": total_students,
        "total_courses": total_courses,
        "total_instructors": total_instructors,
        "recent_courses": recent_courses
    }
    return render(request, "fefu_lab/home.html", ctx)


def about(request):
    return render(request, "fefu_lab/about.html", {"title": "О нас"})


def student_list(request):
    """Список студентов с поиском и фильтрацией"""
    students = Student.objects.filter(is_active=True).order_by('last_name', 'first_name')
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    faculty = request.GET.get('faculty', '')
    if faculty:
        students = students.filter(faculty=faculty)
    
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Студенты',
        'page_obj': page_obj,
        'search_query': search_query,
        'faculty': faculty,
        'faculty_choices': Student.FACULTY_CHOICES
    }
    return render(request, 'fefu_lab/student_list.html', context)


def student_detail(request, student_id):
    """Детальная информация о студенте из БД"""
    student = get_object_or_404(
        Student.objects.prefetch_related('enrollments__course'),
        pk=student_id,  # используем student_id из URL
        is_active=True
    )
    
    enrollments = student.enrollments.filter(status='ACTIVE').select_related('course')
    
    context = {
        'title': f'{student.full_name}',
        'student': student,
        'student_id': student_id,  # для совместимости со старыми шаблонами
        'enrollments': enrollments
    }
    return render(request, 'fefu_lab/student_detail.html', context)


def course_list(request):
    """Список курсов с поиском и фильтрацией"""
    courses = Course.objects.filter(is_active=True).select_related('instructor').order_by('-created_at')
    
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    level = request.GET.get('level', '')
    if level:
        courses = courses.filter(level=level)
    
    paginator = Paginator(courses, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Курсы',
        'page_obj': page_obj,
        'search_query': search_query,
        'level': level,
        'level_choices': Course.LEVEL_CHOICES
    }
    return render(request, 'fefu_lab/course_list.html', context)


def course_detail(request, course_slug):
    """Детальная информация о курсе из БД"""
    course = get_object_or_404(
        Course.objects.select_related('instructor').prefetch_related('enrollments'),
        slug=course_slug,
        is_active=True
    )
    
    context = {
        'title': course.title,
        'course': course,
        'course_slug': course_slug,  
    }
    return render(request, 'fefu_lab/course_detail.html', context)


def student_register(request):
    """Регистрация нового студента в системе"""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                student = form.save()
                messages.success(
                    request,
                    f'Регистрация прошла успешно! Добро пожаловать, {student.full_name}!'
                )
                return redirect('fefu_lab:student_detail', student_id=student.pk)
            except Exception as e:
                messages.error(request, f'Ошибка при регистрации: {str(e)}')
    else:
        form = StudentRegistrationForm()
    
    context = {
        'title': 'Регистрация студента',
        'form': form
    }
    return render(request, 'fefu_lab/student_register.html', context)


def enroll_student(request, course_slug):
    """Запись студента на курс"""
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            try:
                enrollment = form.save()
                messages.success(
                    request,
                    f'Студент {enrollment.student.full_name} успешно записан на курс {enrollment.course.title}!'
                )
                return redirect('fefu_lab:course_detail', course_slug=course_slug)
            except Exception as e:
                messages.error(request, f'Ошибка при записи: {str(e)}')
    else:
        form = EnrollmentForm(initial={'course': course})
    
    context = {
        'title': f'Запись на курс: {course.title}',
        'form': form,
        'course': course
    }
    return render(request, 'fefu_lab/enrollment.html', context)

def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
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
