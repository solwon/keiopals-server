# Generated by Django 3.1.4 on 2021-01-07 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_main', '0011_auto_20210107_2217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='comments',
        ),
    ]
