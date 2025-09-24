from django.contrib import admin
from .models import Nutrient, DishCompositionNutrients, DishCompositionRequest, Dish

# Register your models here.

admin.site.register(Nutrient)
admin.site.register(DishCompositionNutrients)
admin.site.register(DishCompositionRequest)

admin.site.register(Dish)