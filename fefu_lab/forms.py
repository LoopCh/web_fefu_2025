from django import forms
from django.core.exceptions import ValidationError
from .models import UserProfile

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


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        validate_min_length(username, 1, "Логин обязателен")
        if UserProfile.objects.filter(username__iexact=username.strip()).exists():
            raise ValidationError("Пользователь с таким логином уже существует")
        return username.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if UserProfile.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email

    def clean_password(self):
        pwd = self.cleaned_data.get('password', '')
        if len(pwd) < 8:
            raise ValidationError("Пароль должен быть не короче 8 символов")
        return pwd

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Пароли не совпадают")
        return cleaned
