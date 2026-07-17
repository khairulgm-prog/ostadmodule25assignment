from django.contrib import admin
from .models import CustomUserManager, CustomUser, Doctor, Appointment, Bill

# Register your models here.
admin.site.register(Doctor),
admin.site.register(Appointment),
#admin.site.register(CustomUserManager),
admin.site.register(CustomUser),
admin.site.register(Bill)
