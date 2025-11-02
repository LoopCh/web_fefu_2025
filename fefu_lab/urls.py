from django.urls import path
from . import views

app_name = 'fefu_lab'

urlpatterns = [
    # Главная и о нас (без изменений)
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    
    # Студенты (обновлено для работы с БД)
    path('students/', views.student_list, name='student_list'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/register/', views.student_register, name='student_register'),
    
    # Курсы (обновлено для работы с БД)
    path('courses/', views.course_list, name='course_list'),
    path('course/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:course_slug>/enroll/', views.enroll_student, name='enroll_student'),
    
    # Обратная связь и авторизация (без изменений)
    path('feedback/', views.feedback, name='feedback'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
]
