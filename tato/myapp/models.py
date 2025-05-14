from django.db import models
from django.utils import timezone
# Create your models here.
class user(models.Model):
    id = models.CharField(max_length=20,primary_key=True)
    email = models.EmailField(default= None)
from django.db import models

class Camera(models.Model):
    CAMERA_TYPES = [
        ('USB', 'USB Camera'),
        ('IP', 'IP Camera'),
        ('RTSP', 'RTSP Stream'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom")
    location = models.CharField(max_length=200, verbose_name="Emplacement")
    camera_type = models.CharField(
        max_length=50, 
        choices=CAMERA_TYPES,
        verbose_name="Type"
    )
    source = models.CharField(
        max_length=500,
        verbose_name="Source",
        help_text="Numéro de périphérique (0, 1, etc.) ou URL RTSP"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_camera_type_display()})"

class CameraLog(models.Model):
    camera = models.ForeignKey(
        Camera, 
        on_delete=models.CASCADE,
        related_name='logs'
    )
    status = models.CharField(
        max_length=20,
        choices=[('online', 'En ligne'), ('offline', 'Hors ligne')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    face_label = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    enrolled_at = models.DateTimeField(default=timezone.now)    
    consent_read = models.BooleanField(default=False)
    consent_data = models.BooleanField(default=False)
    consent_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class RecognitionHistory(models.Model):
    user = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    recognized = models.BooleanField(default=False)
    confidence = models.FloatField()
    camera_source = models.CharField(max_length=100, blank=True)  # si tu veux indiquer quelle caméra
    image_path = models.CharField(max_length=255, blank=True)     # optionnel : chemin vers la capture

    def __str__(self):
        return f"{self.user or 'Inconnu'} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

