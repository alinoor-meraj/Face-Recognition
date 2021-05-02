from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import TextInput, EmailInput, Select, FileInput
from .models import PersonName


class AddPersonsForm(forms.ModelForm):
    class Meta:
        model = PersonName
        fields = ('person_name',)