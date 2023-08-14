import random
import time
from MainApp.models import EventsMembers, ClassRoom
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User

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


def f(instance, filename):
    ext = filename.split('.')[-1]
    return '{}.{}'.format(f"avatars/{random.randint(1, 1000000)}_{str(time.time())}", ext)


class Account(AbstractBaseUser):
    ROLES = [
        ("admin", "Администратор"),
        ("teacher", "Учитель"),
        ("parent", "Родитель"),
        ("student", "Ученик"),
        ("methodist", "Методист"),
        ("director", "Директор"),
        ("head_teacher", "Завуч"),
        ("psychologist", "Психолог"),
    ]
    PECULARITY_CHOICE = [
        ("handicapped", "инвалидность"),
        ("autism","аутизм")
    ]
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    role = models.TextField(choices=ROLES, null=True, max_length=20)
    first_name = models.CharField(max_length=50, null=True)  # Имя
    second_name = models.CharField(max_length=50, null=True)  # Фамилия
    middle_name = models.CharField(max_length=50, null=True)  # Отчество
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_of_birth = models.DateField(null=True, verbose_name="дата рождения")
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True)
    points = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to=f, null=True, blank=True)
    token = models.CharField(max_length=1000, null=True)
    peculiarity = models.CharField(max_length=1000, null=True, choices=PECULARITY_CHOICE, blank=True)
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

    def stringToColor(self, text):
        hash = 0
        color = ''
        for i in range(len(text)):
            hash = ord(text[i]) + ((hash << 5) - hash)
        for i in range(3):
            value = (hash >> (i * 8)) & 0xFF
            color += ('00' + hex(value)[2:])[-2:]
        return color


    def changeColor(self, HTMLcolor):
        e = self.rgb2hsl(HTMLcolor)
        if (e[0] < 0.55 and e[2] >= 0.5) or (e[0] >= 0.55 and e[2] >= 0.75):
            fc = '000000'  # черный
        else:
            fc = 'FFFFFF'  # белый
        return fc
        # далее меняем цвет, где это необходимо

    def rgb2hsl(self, HTMLcolor):
        r = int(HTMLcolor[0:2], 16) / 255
        g = int(HTMLcolor[2:4], 16) / 255
        b = int(HTMLcolor[4:6], 16) / 255
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        l = (max_val + min_val) / 2
        if max_val == min_val:
            h = s = 0
        else:
            d = max_val - min_val
            s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
            if max_val == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        return [h, s, l]

    def gen_avatar(self):
        bg = self.stringToColor(self.full_name())

        fc = self.changeColor(bg)
        avatar_url = f"https://ui-avatars.com/api/?name={self.first_name}+{self.middle_name}&background={bg}&color={fc}"
        return avatar_url

    def get_avatar(self):
        #print("test")
        if self.avatar:
            return self.avatar.url
        else:
            text = self.first_name + " " + self.middle_name
            hash = 0
            color = ''
            for i in range(len(text)):
                hash = ord(text[i]) + ((hash << 5) - hash)
            for i in range(3):
                value = (hash >> (i * 8)) & 0xFF
                color += ('00' + hex(value)[2:])[-2:]
            bg = color

            r = int(bg[0:2], 16) / 255
            g = int(bg[2:4], 16) / 255
            b = int(bg[4:6], 16) / 255
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            l = (max_val + min_val) / 2
            if max_val == min_val:
                h = s = 0
            else:
                d = max_val - min_val
                s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
                if max_val == r:
                    h = (g - b) / d + (6 if g < b else 0)
                elif max_val == g:
                    h = (b - r) / d + 2
                else:
                    h = (r - g) / d + 4
                h /= 6
            e = [h, s, l]
            if (e[0] < 0.55 and e[2] >= 0.5) or (e[0] >= 0.55 and e[2] >= 0.75):
                fc = '000000'  # черный
            else:
                fc = 'FFFFFF'  # белый

            avatar_url = f"https://ui-avatars.com/api/?name={self.first_name}+{self.middle_name}&background={bg}&color={fc}"
            return avatar_url


class Connections(models.Model):
    ip = models.CharField(max_length=50)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=1000, null=True)
    device_browser = models.CharField(max_length=1000, null=True, blank=True)
    device_system = models.CharField(max_length=1000, null=True, blank=True)
    last_activity = models.DateTimeField(null=True, auto_now_add=True)
