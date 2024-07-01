from django.contrib import admin
from app.models import User_model,room_model
# Register your models here.

admin.site.register([User_model,room_model])
