from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return HttpResponse("Главная страница")

def about(request):
    return HttpResponse("Страница о нас")

def student_detail(request, student_id):
    return HttpResponse(f"Информация о студенте с id {student_id}")

def course_detail(request, course_slag):
    return HttpResponse(f"Информация о курсе с slug: '{course_slag}'")