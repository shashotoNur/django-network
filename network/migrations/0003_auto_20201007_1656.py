# Generated by Django 3.0.4 on 2020-10-07 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_follow_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='timestamp',
            field=models.DateTimeField(),
        ),
    ]