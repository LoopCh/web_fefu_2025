from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailBackend(BaseBackend):
    """
    Кастомный backend для аутентификации по email
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Аутентификация пользователя по email и паролю
        """
        if username is None or password is None:
            return None
        
        try:
            # Ищем пользователя по email
            user = User.objects.get(Q(email=username) | Q(username=username))
        except User.DoesNotExist:
            # Запускаем хеширование пароля для защиты от timing атак
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Если несколько пользователей, возвращаем первого
            user = User.objects.filter(Q(email=username) | Q(username=username)).first()
        
        # Проверяем пароль
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Получение пользователя по ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    def user_can_authenticate(self, user):
        """
        Проверка, может ли пользователь аутентифицироваться
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None
