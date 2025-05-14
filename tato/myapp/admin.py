from django.contrib import admin
from .models import user
from .models import Department, UserProfile, RecognitionHistory

admin.site.register(user)
admin.site.register(Department)
admin.site.register(UserProfile)
admin.site.register(RecognitionHistory)
# Register your models here.
