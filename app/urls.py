from django.urls import path, re_path
from app import views
from .views import *
urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    re_path(r'^.*\.html', views.pages, name='pages'),

    # The home page
    path('', views.index, name='home'),
    # path('create-dataset', create_dataset, name='create-dataset'),
    # path('detect', detect, name='detect'),
    path('train', train, name='train'),
    path('live_cam', live_cam, name='live_cam'),
    path('face-detected-list/', face_detected_list, name='face-detected-list'),
    path('video_feed', views.video_feed, name='video_feed'),
    path('new_face_data', views.new_face_data, name='new_face_data'),
]
