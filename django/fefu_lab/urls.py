from django.urls import path
from . import views

app_name = 'fefu_lab'

urlpatterns = [
    # Главная и о нас
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    
    # Студенты
    path('students/', views.student_list, name='student_list'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    
    # Курсы
    path('courses/', views.course_list, name='course_list'),
    path('course/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:course_slug>/enroll/', views.enroll_student, name='enroll_student'),
    
    # Обратная связь
    path('feedback/', views.feedback, name='feedback'),
    
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Личные кабинеты
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
]
