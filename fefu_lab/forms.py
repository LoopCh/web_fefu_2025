from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Student, Enrollment, Course


def validate_min_length(value: str, n: int, msg: str):
    if value is None or len(value.strip()) < n:
        raise ValidationError(msg)


class FeedbackForm(forms.Form):
    name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True
    )
    subject = forms.CharField(
        label='Тема',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    message = forms.CharField(
        label='Текст сообщения',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        required=True
    )

    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        validate_min_length(name, 2, "Имя должно содержать минимум 2 символа")
        return name.strip()

    def clean_message(self):
        msg = self.cleaned_data.get('message', '')
        validate_min_length(msg, 10, "Текст сообщения должен быть не короче 10 символов")
        return msg.strip()


class UserRegistrationForm(forms.ModelForm):
    """Форма регистрации пользователя с профилем"""
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    faculty = forms.ChoiceField(
        label='Факультет',
        choices=Student.FACULTY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        label='Роль',
        choices=Student.ROLE_CHOICES,
        initial='STUDENT',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email'
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Пароли не совпадают.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # используем email как username
        user.set_password(self.cleaned_data['password'])  # хешируем пароль
        
        if commit:
            user.save()
            # Обновляем профиль студента
            profile = user.student_profile
            profile.faculty = self.cleaned_data['faculty']
            profile.role = self.cleaned_data['role']
            profile.save()
        
        return user


class EmailAuthenticationForm(AuthenticationForm):
    """Форма входа по email"""
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autofocus': True})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class ProfileEditForm(forms.ModelForm):
    """Форма редактирования профиля"""
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Student
        fields = ['phone', 'bio', 'faculty', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'phone': 'Телефон',
            'bio': 'О себе',
            'faculty': 'Факультет',
            'avatar': 'Аватар'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            profile.save()
        
        return profile


class EnrollmentForm(forms.ModelForm):
    """Форма записи на курс"""
    class Meta:
        model = Enrollment
        fields = ['student', 'course']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'student': 'Студент',
            'course': 'Курс'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_active=True)
        self.fields['course'].queryset = Course.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        course = cleaned_data.get('course')
        
        if student and course:
            if Enrollment.objects.filter(student=student, course=course).exists():
                raise ValidationError('Этот студент уже записан на данный курс.')
            
            if not course.has_available_seats:
                raise ValidationError('На этом курсе больше нет свободных мест.')
        
        return cleaned_data
