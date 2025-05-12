from django.urls import path
from . import views

urlpatterns = [
    path('webcam/', views.webcam_view, name='webcam_stream'),
    path('update_camera_mode/', views.update_camera_mode, name='update_camera_mode'),
    path('webcam/stream/', views.webcam_stream, name='webcam_stream'), 
    path('cameras/add/', views.add_camera, name='add_camera'),
    path('cameras/preview/', views.camera_preview, name='camera_preview'),
    ]