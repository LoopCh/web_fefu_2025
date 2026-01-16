from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps


def role_required(*roles):
    """
    Декоратор для проверки роли пользователя
    Использование: @role_required('TEACHER', 'ADMIN')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('fefu_lab:login')
            
            if not hasattr(request.user, 'student_profile'):
                return redirect('fefu_lab:index')
            
            if request.user.student_profile.role in roles:
                return view_func(request, *args, **kwargs)
            
            return redirect('fefu_lab:index')
        
        return wrapper
    return decorator


def student_required(view_func):
    """Декоратор для проверки роли студента"""
    return role_required('STUDENT')(view_func)


def teacher_required(view_func):
    """Декоратор для проверки роли преподавателя"""
    return role_required('TEACHER', 'ADMIN')(view_func)


def admin_required(view_func):
    """Декоратор для проверки роли администратора"""
    return role_required('ADMIN')(view_func)
