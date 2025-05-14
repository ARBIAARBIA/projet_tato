from django.urls import path
from . import views

urlpatterns = [
    path('webcam/', views.webcam_view, name='webcam_stream'),
    path('update_camera_mode/', views.update_camera_mode, name='update_camera_mode'),
    path('webcam/stream/', views.webcam_stream, name='webcam_stream'), 
    path('cameras/add/', views.add_camera, name='add_camera'),
    path('cameras/preview/', views.camera_preview, name='camera_preview'),
    path('enrollment/', views.enrollment_view, name='enrollment'),
    path('api/enroll/', views.enroll_api, name='enroll'),
    path('api/retrain/', views.retrain_api, name='retrain'),
    path('recognize/', views.recognize_face, name='recognize_face'),
    path('realtime/', views.recognition_view, name='realtime_recognition'),
    path('history/', views.recognition_history_view, name='recognition_history'),

    ]