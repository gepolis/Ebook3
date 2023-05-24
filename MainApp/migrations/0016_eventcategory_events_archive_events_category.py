# Generated by Django 4.2 on 2023-05-24 19:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0015_eventsmembers_points'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Event category',
                'verbose_name_plural': 'Event categories',
            },
        ),
        migrations.AddField(
            model_name='events',
            name='archive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='events',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category', to='MainApp.eventcategory'),
        ),
    ]