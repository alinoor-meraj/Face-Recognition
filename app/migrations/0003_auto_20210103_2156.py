# Generated by Django 3.1.4 on 2021-01-03 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20210103_0958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facedetectedtime',
            name='detected_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='facedetectedtime',
            name='detected_time',
            field=models.TimeField(),
        ),
    ]