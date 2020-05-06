from django.contrib import admin
from . import models

admin.site.register(models.Active)
admin.site.register(models.Operation)
admin.site.register(models.Period)
admin.site.register(models.Profile)