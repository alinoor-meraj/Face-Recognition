# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    address = models.CharField(max_length=100,null=True,blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    postal_code = models.PositiveIntegerField(default=0000)
    about = models.CharField(max_length=100,null=True,blank=True)
    image = models.ImageField(default='default.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username}'


class UserAlert(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    sms_mobile_number = models.PositiveIntegerField(null=True)
    sms_body = models.CharField(max_length=100,null=True,blank=True)
    alert_email = models.EmailField(max_length=254,null=True,blank=True)
    alert_email_subject = models.CharField(max_length=100,null=True,blank=True)
    alert_email_body = models.TextField(max_length=1024,null=True,blank=True)

    def __str__(self):
        return f'{self.user.username}'



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserAlert.objects.create(user=instance)
        post_save.connect(create_profile, sender=User)