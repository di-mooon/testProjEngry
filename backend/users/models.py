import uuid

from core.base_models import AbstractBaseModel
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager):
    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError("The given phone must be set")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    class UserRoles(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        SERVICE = 'SERVICE', 'Service'
        USER = 'USER', 'User'

    username = models.CharField(max_length=120, blank=True, default='')
    full_name = models.CharField(max_length=220, blank=True, null=True)
    phone = models.BigIntegerField('Телефон', unique=True, db_index=True)

    role = models.CharField('Роль', max_length=20, choices=UserRoles.choices, default=UserRoles.USER)
    tg_id = models.BigIntegerField('Телеграм ID', db_index=True, unique=True, blank=True, null=True)
    tg_username = models.CharField('Телеграм Username', max_length=300, blank=True, null=True)
    whatsapp_id = models.CharField('WhatsApp Username', max_length=300, blank=True, null=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ('password',)

    objects = UserManager()

    def __str__(self):
        return f'{self.phone}'

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'


class TgUserToken(AbstractBaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        blank=True, null=True,
        related_name='tg_tokens'
    )
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    activated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.token}'

    class Meta:
        verbose_name = 'Токен активации телеграм'
        verbose_name_plural = 'Токены активации телеграм'


class ConfirmCodeType(models.TextChoices):
    REGISTER = 'REGISTER', 'регистрация'
    AUTH = 'AUTH', 'авторизация'
    RESET_PASSWORD = 'RESET_PASSWORD', 'сброс пароля'
