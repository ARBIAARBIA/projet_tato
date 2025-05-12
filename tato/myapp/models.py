from django.db import models

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