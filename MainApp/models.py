import random
import time

import django.contrib.auth
from django.db import models
from django.core import validators

Account = "Accounts.account"
from multiselectfield import MultiSelectField
import uuid


class EventsMembers(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    points = models.IntegerField(validators=[
        validators.MinValueValidator(0),
        validators.MaxValueValidator(100)
    ], null=True)
    is_active = models.BooleanField(default=False)


class ClassRoomsNumber(models.Model):
    name = models.CharField(max_length=255)
    value = models.IntegerField()

    def __str__(self):
        return self.name


class EventCategory(models.Model):
    name = models.CharField(max_length=255)
    methodists = models.ManyToManyField(Account, limit_choices_to={"role": "methodist"}, blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Катигории"

    def __str__(self):
        return self.name


class Subjects(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return self.name


class Events(models.Model):
    CLASSROOM = [
        ("0", "Детский сад"),
        ("1", "1 класс"),
        ("2", "2 класс"),
        ("3", "3 класс"),
        ("4", "4 класс"),
        ("5", "5 класс"),
        ("6", "6 класс"),
        ("7", "7 класс"),
        ("8", "8 класс"),
        ("9", "9 класс"),
        ("10", "10 класс"),
        ("11", "11 класс")
    ]
    TYPES = [
        ("subject", "Предметное"),
        ("methodist", "Методическое")
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2550)

    start_date = models.DateTimeField(auto_now=False)
    end_date = models.DateTimeField(auto_now=False)

    classroom_number = models.CharField(max_length=255, choices=CLASSROOM, null=True)
    type = models.CharField(max_length=255, choices=TYPES, null=True, default="subject")

    archive = models.BooleanField(default=False)

    image = models.ImageField(upload_to="images", null=True)

    subject = models.ForeignKey(Subjects, on_delete=models.SET_NULL, null=True, related_name="subject", blank=True)
    category = models.ForeignKey(EventCategory, related_name="category", on_delete=models.SET_NULL, null=True,
                                 blank=True)
    organizer = models.ForeignKey(Account, on_delete=models.SET_NULL, related_name="organizer", null=True)
    building = models.ForeignKey("Accounts.building", on_delete=models.SET_NULL, related_name="building", null=True)

    volunteer = models.ManyToManyField(EventsMembers, related_name="volunteers", blank=True)

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def __str__(self):
        return f"{self.name} - {self.volunteer}"


def f(instance, filename):
    ext = filename.split('.')[-1]
    return '{}.{}'.format(f"photo_reports/{instance.event.pk}/{random.randint(1, 1000000)}_{str(time.time())}", ext)


class PhotoReport(models.Model):
    image = models.ImageField(upload_to=f)
    event = models.ForeignKey(Events, on_delete=models.CASCADE, null=True)
    uploaded = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    author = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)


class ClassRoom(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    teacher = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="teacher", null=True)
    member = models.ManyToManyField(Account, related_name="students", blank=True)
    classroom = models.IntegerField()
    parallel = models.CharField(max_length=1)

    def invite_url(self):
        return f"https://mysite.com:8000/lk/classroom/invite/{self.uuid}/"

    def __str__(self):
        return f"{self.classroom}\"{self.parallel}\""

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"


class TeacherInviteEvent(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="event_classroom")
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name="event_teacher")

    class Meta:
        verbose_name = "Приглашение на мероприятие"
        verbose_name_plural = "Приглашения на мероприятия"


