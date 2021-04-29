from django.contrib import admin
from .models import TubbrUser, Event

# Register your models here.

admin.site.register(TubbrUser)
admin.site.register(Event)