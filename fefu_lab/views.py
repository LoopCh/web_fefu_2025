from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    ctx = {"title": "Главная", "user": None}
    return render(request, "fefu_lab/home.html", ctx)

def about(request):
    return render(request, "fefu_lab/about.html", {"title": "О нас"})

def student_detail(request, student_id):
    return render(request, "fefu_lab/student_detail.html", {"student_id": student_id})

def course_detail(request, course_slug):
    return render(request, "fefu_lab/course_detail.html", {"course_slug": course_slug})

def page_not_found(request, exception):
    return render(request, '404.html', status=404)