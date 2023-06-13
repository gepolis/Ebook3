import time

from django.db import models

from Accounts.models import Account


class Notications(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    user = models.ForeignKey(Account, on_delete=models.CharField)
    created = models.IntegerField(blank=True,null=True)
    sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.created = round(time.time())
        super(Notications, self).save(*args, **kwargs)