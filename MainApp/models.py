from django.db import models
from django.core import validators
from Accounts.models import Account, Building
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
class Events(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2550)
    start_date = models.DateTimeField(auto_now=False)
    end_date = models.DateTimeField(auto_now=False)
    classroom_number =models.ManyToManyField(ClassRoomsNumber)
    volunteer = models.ManyToManyField(EventsMembers)
    organizer = models.ForeignKey(Account, on_delete=models.SET_NULL, related_name="orgonizaer",null=True)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, related_name="building", null=True)
    image = models.ImageField(upload_to="images", null=True)
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return f"{self.name} - {self.volunteer}"

class ClassRoom(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    teacher = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="teacher")
    member = models.ManyToManyField(Account, related_name="students", blank=True)
    classroom = models.IntegerField()
    parallel = models.CharField(max_length=1)

    def invite_url(self):
        return f"https://mysite.com:8000/lk/classroom/invite/{self.uuid}/"

class TeacherInviteEvent(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="event_classroom")
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name="event")
