from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Instructor, Course, Enrollment


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'faculty', 'is_active', 'created_at']
    list_filter = ['is_active', 'faculty', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    list_editable = ['is_active']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Дополнительная информация', {
            'fields': ('birth_date', 'faculty', 'is_active')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('enrollments')


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'specialization', 'degree', 'is_active', 'courses_count']
    list_filter = ['is_active', 'degree', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'specialization']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'courses_count']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Профессиональная информация', {
            'fields': ('specialization', 'degree', 'bio')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'courses_count'),
            'classes': ('collapse',)
        }),
    )
    
    def courses_count(self, obj):
        count = obj.courses.filter(is_active=True).count()
        return format_html('<strong>{}</strong>', count)
    courses_count.short_description = 'Активных курсов'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'level', 'duration', 'enrolled_students', 'max_students', 'price', 'is_active']
    list_filter = ['is_active', 'level', 'created_at']
    search_fields = ['title', 'description', 'instructor__last_name']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'enrolled_students']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Параметры курса', {
            'fields': ('duration', 'level', 'instructor', 'max_students', 'price')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Статистика', {
            'fields': ('enrolled_students', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def enrolled_students(self, obj):
        count = obj.enrollments.filter(status='ACTIVE').count()
        if count >= obj.max_students:
            color = 'red'
        elif count >= obj.max_students * 0.8:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/{}</span>',
            color, count, obj.max_students
        )
    enrolled_students.short_description = 'Записано студентов'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'enrolled_at']
    list_filter = ['status', 'enrolled_at', 'course__level']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']
    list_editable = ['status']
    date_hierarchy = 'enrolled_at'
    readonly_fields = ['enrolled_at']
    raw_id_fields = ['student', 'course']
    
    fieldsets = (
        ('Информация о записи', {
            'fields': ('student', 'course', 'status')
        }),
        ('Даты', {
            'fields': ('enrolled_at',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student', 'course')
