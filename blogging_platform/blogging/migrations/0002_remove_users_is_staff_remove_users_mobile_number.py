# Generated by Django 4.2.4 on 2023-09-04 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogging', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='users',
            name='mobile_number',
        ),
    ]
