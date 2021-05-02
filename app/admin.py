from django.contrib import admin
from .models import *
# Register your models here.
class PersonNameAdmin(admin.ModelAdmin):
    list_display = ['id', 'person_name', ]

admin.site.register(PersonName,PersonNameAdmin)

class FaceDetectedTimeAdmin(admin.ModelAdmin):
    list_display = ['detected_face', 'detected_time', 'detected_date', ]

admin.site.register(FaceDetectedTime,FaceDetectedTimeAdmin)