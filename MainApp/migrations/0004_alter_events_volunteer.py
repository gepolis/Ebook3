# Generated by Django 4.0 on 2023-07-06 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0003_alter_eventcategory_options_alter_classroom_teacher_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='volunteer',
            field=models.ManyToManyField(related_name='volunteers', to='MainApp.EventsMembers'),
        ),
    ]
