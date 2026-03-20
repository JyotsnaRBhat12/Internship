from django.contrib import admin
from .models import Note, SharedLink

admin.site.register(Note)
admin.site.register(SharedLink)