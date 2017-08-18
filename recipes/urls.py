from django.conf.urls import url
from django.contrib import admin
from .views import (
	recipe_list,
	recipe_list_testing1,
	recipe_update,
	recipe_ingredients_formset_update,
	recipe_confirm,
	recipe_delete,
	recipe_detail,
	recipeposition_confirm,
	recipeposition_update,
	recipeposition_delete,
	recipe_formset_update,
	recipe_formset_create,
	ingredient_recipe_update,
	recipe_testing
	)

urlpatterns = [
	url(r'^testing/$', recipe_testing , name='recipe_testing'),
	url(r'^$', recipe_list, name='list'),
	url(r'^edit/$', recipe_formset_update , name='formsetedit'),
	url(r'^create/$', recipe_formset_create , name='formsetcreate'),
	url(r'^test1/', recipe_list_testing1, name='test1'),
	url(r'^(?P<slug>[\w-]+)/edit/$', recipe_update, name='update'),
	url(r'^(?P<slug>[\w-]+)/editbulk/$', recipe_ingredients_formset_update, name='updateingredientbulk'),
	url(r'^(?P<slug>[\w-]+)/detail/$', recipe_detail, name='detail'),
	url(r'^(?P<slug>[\w-]+)/delete/$', recipe_delete, name='delete'),
	url(r'^(?P<slug>[\w-]+)/confirm/$', recipe_confirm, name='confirm'),


	url(r'^pos/(?P<slug>[\w-]+)/edit/$', recipeposition_update, name='updatepos'),
	url(r'^pos/(?P<slug>[\w-]+)/delete/$', recipeposition_delete, name='deletepos'),
	url(r'^pos/(?P<slug>[\w-]+)/confirm/$', recipeposition_confirm, name='confirmpos'),

	url(r'^(?P<slug>[\w-]+)/ing_update/$', ingredient_recipe_update, name='ing_recipe_upd'),
]