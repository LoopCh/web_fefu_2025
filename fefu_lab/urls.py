from django.urls import path
from . import views

app_name = 'fefu_lab'

urlpatterns = [
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('course/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('feedback/', views.feedback, name='feedback'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login')
]