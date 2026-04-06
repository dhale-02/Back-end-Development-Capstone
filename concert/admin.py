from django.contrib import admin
from .models import Concert, ConcertAttending

admin.site.register(Concert)
admin.site.register(ConcertAttending)
