# Generated by Django 4.2 on 2023-05-21 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PersonalArea', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notications',
            name='viewed',
            field=models.BooleanField(default=False),
        ),
    ]
