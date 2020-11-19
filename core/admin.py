from django.contrib import admin

from .models import Category, Cuisine, AdditionalService, Place


admin.site.register([
    Category,
    Cuisine,
    AdditionalService,
    Place
    ])