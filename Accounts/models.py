import random
import time
from MainApp.models import EventsMembers, ClassRoom
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.core import validators


class MyAccountManager(BaseUserManager):
    def create_user(self, email=None, second_name=None, first_name=None, middle_name=None, password=None,
                    username: str = None):
        if username is None:
            raise ValueError("User must have an username.")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            second_name=second_name,
            first_name=first_name,
            middle_name=middle_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, second_name, first_name, middle_name):
        user = self.create_user(email=self.normalize_email(email),
                                username=username,
                                password=password,
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
        ("methodist", "Методист")
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
    date_of_birth = models.DateField(null=True, verbose_name="дата рождения")
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True)
    points = models.IntegerField(default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', "second_name", "first_name", "middle_name"]

    objects = MyAccountManager()

    def __str__(self):
        return f"{self.second_name} {self.first_name} {self.middle_name}"

    def full_name(self):
        return f"{self.second_name} {self.first_name} {self.middle_name}"

    def has_classroom(self):
        if self.role == "teacher":
            if ClassRoom.objects.all().filter(teacher=self).exists():
                return True
        elif self.role == "student":
            if ClassRoom.objects.all().filter(member=self).exists():
                return True
        return False
    def get_classroom(self):
        if not self.has_classroom():
            return False
        if self.role == "teacher":
            return ClassRoom.objects.get(teacher=self)
        elif self.role == "student":
            return ClassRoom.objects.get(member=self)
    def get_events(self):
        events = EventsMembers.all().filter(user=self)
        return events
    def get_events_count(self):
        events = EventsMembers.all().filter(user=self)
        return len(events)
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
