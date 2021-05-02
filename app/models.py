from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class PersonName(models.Model):
    person_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.person_name}'


class FaceDetectedTime(models.Model):
    detected_face = models.CharField(max_length=100)
    detected_date = models.DateField(auto_now=True)
    detected_time = models.TimeField(auto_now=True)

    def __str__(self):
        return f'{self.detected_face} '

