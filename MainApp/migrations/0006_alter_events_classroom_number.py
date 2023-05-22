# Generated by Django 4.2 on 2023-05-16 22:25

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0005_alter_events_classroom_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='classroom_number',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('0', 'Детский сад'), ('1', '1 класс'), ('2', '2 класс'), ('3', '3 класс'), ('4', '4 класс'), ('5', '5 класс'), ('6', '6 класс'), ('7', '7 класс'), ('8', '8 класс'), ('9', '9 класс'), ('10', '10 класс'), ('11', '11 класс')], max_length=12),
        ),
    ]
