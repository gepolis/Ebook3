# Generated by Django 4.2 on 2023-05-19 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0026_alter_otps_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otps',
            name='code',
            field=models.IntegerField(default=976638),
        ),
    ]
