from django import forms
from .models import Camera

class CameraForm(forms.ModelForm):
    class Meta:
        model = Camera
        fields = ['name', 'location', 'camera_type', 'source', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Camera Principale'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Entrée Principale'
            }),
            'camera_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 0 for default webcam or rtsp://url'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Nom de la Caméra',
            'location': 'Emplacement',
            'camera_type': 'Type de Caméra',
            'source': 'Source',
            'is_active': 'Active'
        }
        help_texts = {
            'source': "Pour les caméras USB, utiliser un numéro (0, 1, etc.). Pour IP/RTSP, entrer l'URL complète."
        }