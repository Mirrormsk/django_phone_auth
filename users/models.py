import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    username = None
    phone = models.CharField(unique=True, max_length=35, verbose_name='номер телефона')
    email = models.EmailField(unique=True, verbose_name='почта', **NULLABLE)
    uid = models.UUIDField(default=uuid.uuid4, editable=False)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []
