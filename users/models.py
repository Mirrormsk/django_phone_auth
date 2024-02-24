import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    username = None
    phone = models.CharField(unique=True, max_length=35, verbose_name='номер телефона')
    email = models.EmailField(unique=True, verbose_name='почта', **NULLABLE)
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, verbose_name='имя', **NULLABLE)
    last_name = models.CharField(max_length=100, verbose_name='фамилия', **NULLABLE)
    otp_code = models.CharField(max_length=4, verbose_name='одноразовый код подтверждения', **NULLABLE)
    is_active = models.BooleanField(default=False, verbose_name='активен')
    last_code_sent_time = models.DateTimeField(verbose_name='последняя отправка кода', **NULLABLE)
    invite_code = models.CharField(max_length=6, verbose_name='инвайт-код', **NULLABLE)
    invited_by = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='пригласил', **NULLABLE,
                                   related_name='invited_users')

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []
