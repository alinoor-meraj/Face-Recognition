# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include  # add this

admin.site.site_header = "Smart Security Admin"
admin.site.site_title = "Smart Security Admin"
admin.site.index_title = "Smart Security administration"


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("authentication.urls")),  # add this
    path("", include("app.urls"))  # add this
]
