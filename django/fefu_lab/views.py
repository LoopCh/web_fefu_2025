from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .forms import (
    FeedbackForm, UserRegistrationForm, EmailAuthenticationForm,
    EnrollmentForm, ProfileEditForm
)
from .models import Student, Course, Instructor, Enrollment
from .decorators import role_required, student_required, teacher_required, admin_required


def home(request):
    total_students = Student.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_instructors = Instructor.objects.filter(is_active=True).count()
    recent_courses = Course.objects.filter(is_active=True).select_related('instructor').order_by('-created_at')[:3]
    
    ctx = {
        "title": "Главная",
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
    students = Student.objects.filter(is_active=True).select_related('user').order_by('user__last_name', 'user__first_name')
    
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
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
    """Детальная информация о студенте"""
    student = get_object_or_404(
        Student.objects.prefetch_related('enrollments__course').select_related('user'),
        pk=student_id,
        is_active=True
    )
    
    enrollments = student.enrollments.filter(status='ACTIVE').select_related('course')
    
    context = {
        'title': f'{student.full_name}',
        'student': student,
        'student_id': student_id,
        'enrollments': enrollments
    }
    return render(request, 'fefu_lab/student_detail.html', context)


def course_list(request):
    """Список курсов"""
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
    """Детальная информация о курсе"""
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


@login_required(login_url='/login/')
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
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend='fefu_lab.backends.EmailBackend')
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            return redirect('fefu_lab:profile')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'fefu_lab/registration/register.html', {
        'form': form,
        'title': 'Регистрация'
    })


def login_view(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('fefu_lab:profile')
    
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Добро пожаловать, {user.first_name}!')
                next_url = request.GET.get('next', 'fefu_lab:profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный email или пароль.')
        else:
            messages.error(request, 'Неверный email или пароль.')
    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'fefu_lab/registration/login.html', {
        'form': form,
        'title': 'Вход'
    })


@login_required(login_url='/login/')
def logout_view(request):
    """Выход из системы"""
    auth_logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('fefu_lab:index')


@login_required(login_url='/login/')
def profile(request):
    """Профиль пользователя"""
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, 'Профиль не найден.')
        return redirect('fefu_lab:index')
    
    profile = request.user.student_profile
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('fefu_lab:profile')
    else:
        form = ProfileEditForm(instance=profile)
    
    context = {
        'title': 'Мой профиль',
        'profile': profile,
        'form': form
    }
    return render(request, 'fefu_lab/registration/profile.html', context)


@login_required(login_url='/login/')
@student_required
def student_dashboard(request):
    """Личный кабинет студента"""
    profile = request.user.student_profile
    enrollments = Enrollment.objects.filter(
        student=profile,
        status='ACTIVE'
    ).select_related('course')
    
    context = {
        'title': 'Личный кабинет',
        'profile': profile,
        'enrollments': enrollments
    }
    return render(request, 'fefu_lab/dashboard/student_dashboard.html', context)


@login_required(login_url='/login/')
@teacher_required
def teacher_dashboard(request):
    """Личный кабинет преподавателя"""
    profile = request.user.student_profile
    # Здесь можно добавить логику для курсов преподавателя
    courses = Course.objects.filter(is_active=True)
    
    context = {
        'title': 'Кабинет преподавателя',
        'profile': profile,
        'courses': courses
    }
    return render(request, 'fefu_lab/dashboard/teacher_dashboard.html', context)


@login_required(login_url='/login/')
@admin_required
def admin_dashboard(request):
    """Панель администратора"""
    profile = request.user.student_profile
    total_users = Student.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    
    context = {
        'title': 'Панель администратора',
        'profile': profile,
        'total_users': total_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments
    }
    return render(request, 'fefu_lab/dashboard/admin_dashboard.html', context)


def page_not_found(request, exception):
    return render(request, '404.html', status=404)
