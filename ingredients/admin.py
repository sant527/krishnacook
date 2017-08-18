from django.contrib import admin

from .models import Ingredient
# Register your models here.

class IngredientModelAdmin(admin.ModelAdmin):
	list_display = ["name", "slug","munit", "rate","updated","timestamp"]
	list_display_links = ["name"]
	search_fields = ["name"]
	class Meta:
		model=Ingredient

admin.site.register(Ingredient, IngredientModelAdmin)

