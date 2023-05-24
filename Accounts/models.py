import random
import time

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.core import validators


class MyAccountManager(BaseUserManager):
    def create_user(self, email=None, age=None, second_name=None, first_name=None, middle_name=None, password=None,
                    username: str = None):
        if username is None:
            raise ValueError("User must have an username.")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            age=age,
            second_name=second_name,
            first_name=first_name,
            middle_name=middle_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, age, second_name, first_name, middle_name):
        user = self.create_user(email=self.normalize_email(email),
                                username=username,
                                password=password,
                                age=age,
                                second_name=second_name,
                                first_name=first_name,
                                middle_name=middle_name
                                )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class Building(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=[("school", "Школа"), ('kg', 'Детский сад')], blank=True)

    def __str__(self):
        return self.name


class Account(AbstractBaseUser):
    ROLES = [
        ("admin", "Администратор"),
        ("teacher", "Учитель"),
        ("parent", "Родитель"),
        ("student", "Ученик"),
    ]
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    role = models.TextField(choices=ROLES, null=True, max_length=10)
    first_name = models.CharField(max_length=50, null=True)  # Имя
    second_name = models.CharField(max_length=50, null=True)  # Фамилия
    middle_name = models.CharField(max_length=50, null=True)  # Отчество
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_of_birth = models.DateField(null=True)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True)
    points = models.IntegerField(default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'age', "second_name", "first_name", "middle_name"]

    objects = MyAccountManager()

    def __str__(self):
        return f"{self.second_name} {self.first_name} {self.middle_name}"

    def full_name(self):
        return f"{self.second_name} {self.first_name} {self.middle_name}"

    def has_perm(self, perm, obj=None):
        return self.is_superuser



    def get_status(self):
        if self.points <= 200:
            return "Медный"
        elif self.points <= 400:
            return "Бронзовый"
        elif self.points <= 600:
            return "Серебряный"
        elif self.points <= 800:
            return "Золотой"
        else:
            return "Бриллиантовый"

    def has_module_perms(self, app_label):
        return True


class OTPs(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    code = models.IntegerField(default=random.randint(100000, 999999))
    is_active = models.BooleanField(default=True)
