# Generated by Django 4.2 on 2023-05-14 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0010_remove_role_perms_remove_account_roles_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otps',
            name='code',
            field=models.IntegerField(default=634118),
        ),
    ]
