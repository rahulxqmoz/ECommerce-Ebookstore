from django.contrib import admin

# Register your models here.

from user_app.models import CustomUser

admin.site.register(CustomUser)