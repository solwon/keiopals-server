# Generated by Django 3.1.4 on 2021-01-03 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_main', '0002_comment_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='no',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
