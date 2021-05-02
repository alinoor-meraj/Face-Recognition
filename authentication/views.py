from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm, AlertUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile, UserAlert

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = 'Sign in with Username'

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:    
                msg = 'Invalid credentials'    
        else:
            msg = 'Error validating the form'    

    return render(request, "accounts/login.html", {"form": form, "msg" : msg})

def register_user(request):

    msg = 'Add your credentials'

    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():

            form.save()
            username = form.cleaned_data.get("username")

            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            user.is_active = False
            user.save()
            return redirect("/login/")
        else:
            msg = 'Form is not valid'    
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg" : msg})


@login_required(login_url='/login')
def user_update(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your Profile information is updated successfully!!!")
            return redirect('user-update')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance = request.user.userprofile)
        #profile_form = ProfileUpdateForm(request.POST, instance = request.user.userprofile)

    context = {
        'user_form': user_form,
        'profile_form':profile_form,    
    }
    return render(request, 'pages/profile.html', context)


@login_required(login_url='/login')
def setting_update(request):
    if request.method == "POST":
        settings_form = AlertUpdateForm(request.POST, instance=request.user.useralert)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, "Your Settings information is updated successfully!!!")
            return redirect('setting-update')
    else:
        settings_form = AlertUpdateForm(instance=request.user.useralert)
    
    alert_email = request.user.useralert.alert_email
    alert_email_subject = request.user.useralert.alert_email_subject
    alert_email_body = request.user.useralert.alert_email_body
    
    # user = User.objects.get(email = request.user.email)
    context = {
        'settings_form': settings_form,
        'alert_email': alert_email,
        'alert_email_subject': alert_email_subject,
        'alert_email_body': alert_email_body,
    }

    return render(request, 'pages/settings.html', context)


@login_required(login_url='/login')  # Check login
def password_change(request):
    url = request.META.get("HTTP_REFERER")
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            msg = messages.error(
                request, 'Error.<br>' + str(form.errors))
            return HttpResponseRedirect(url)
    else:
      
        form = PasswordChangeForm(request.user)
        return render(request, 'user_password.html', {'form': form, 'categories': category, 'setting': setting,
                                                      })




        