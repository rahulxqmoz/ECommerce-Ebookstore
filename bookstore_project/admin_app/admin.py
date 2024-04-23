from django.contrib import admin
from .models import *
# Register your models here.

from user_app.models import CustomUser

admin.site.register(CustomUser)

