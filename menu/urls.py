from django.conf.urls import url
from django.contrib import admin
from .views import (
	menu_list,
	menu_update,
	menu_confirm,
	menu_delete,
	menu_detail,
	menu_detail2,
	menu_detail_ingredient,
	menu_report,
	menu_print,
	menuposition_confirm,
	menuposition_update,
	menuposition_delete,
	menu_total_ingredients,
	menu_recipe_formset_update,
	menu_ingredient_custom_list,
	menu_ingredient_custom_inlineformset_bulk_edit,
	menu_ingredient_custom_recipe_report,
	menu_default_ingredients,
	menu_default_recipes,
	menu_ingredient_custom_recipe_recipe,
	menu_ingredient_custom_recipe_ingredient,
	menu_testing,
	menu_testing2,
	menu_ingredient_default_inlineformset_bulk_edit,
	menu_ingredient_custom_clear_all_values,
	menu_ingredient_custom_sync_with_default
	)

urlpatterns = [
	url(r'^$', menu_list, name='list'),
	url(r'^(?P<slug>[\w-]+)/testing/$', menu_testing, name='testing'),

	url(r'^(?P<slug>[\w-]+)/testing2/$', menu_testing2, name='testing2'),

	url(r'^(?P<slug>[\w-]+)/edit/$', menu_update, name='update'),
	url(r'^(?P<slug>[\w-]+)/editbulk/$', menu_recipe_formset_update, name='updaterecipebulk'),
	
	url(r'^(?P<slug>[\w-]+)/default/detail/$', menu_detail, name='default_detail'),
	url(r'^(?P<slug>[\w-]+)/default/recipes/$', menu_default_recipes, name='default_recipes'),
	url(r'^(?P<slug>[\w-]+)/default/ingredients/$', menu_default_ingredients, name='default_ingredients'),
	url(r'^(?P<slug>[\w-]+)/default/bulkedit$', menu_ingredient_default_inlineformset_bulk_edit, name='defaultingredient_bulkedit'),

	url(r'^(?P<slug>[\w-]+)/detail2/$', menu_detail2, name='detail2'),
	url(r'^(?P<slug>[\w-]+)/detail/ingredient/$', menu_detail_ingredient, name='detail_ingredient'),
	url(r'^(?P<slug>[\w-]+)/report/$', menu_report, name='report'),
	url(r'^(?P<slug>[\w-]+)/print/$', menu_report, name='print'), #menus_report.html
	


	url(r'^(?P<slug>[\w-]+)/delete/$', menu_delete, name='delete'),
	url(r'^(?P<slug>[\w-]+)/confirm/$', menu_confirm, name='confirm'),
	


	url(r'^(?P<slug>[\w-]+)/customingredient/list$', menu_ingredient_custom_list, name='customingredient_list'),
	url(r'^(?P<slug>[\w-]+)/customingredient/bulkedit$', menu_ingredient_custom_inlineformset_bulk_edit, name='customingredient_bulkedit'),

	url(r'^(?P<slug>[\w-]+)/customingredient/clear$', menu_ingredient_custom_clear_all_values, name='customingredient_clear'),	
	url(r'^(?P<slug>[\w-]+)/customingredient/sync$', menu_ingredient_custom_sync_with_default, name='customingredient_sync'),

	url(r'^(?P<slug>[\w-]+)/custom/detail$', menu_ingredient_custom_recipe_report, name='custom_detail'),
	url(r'^(?P<slug>[\w-]+)/custom/recipes$', menu_ingredient_custom_recipe_recipe, name='custom_recipes'),
	url(r'^(?P<slug>[\w-]+)/custom/ingredients$', menu_ingredient_custom_recipe_ingredient, name='custom_ingredients'),

	url(r'^pos/(?P<slug>[\w-]+)/edit/$', menuposition_update, name='updatepos'),
	url(r'^pos/(?P<slug>[\w-]+)/delete/$', menuposition_delete, name='deletepos'),
	url(r'^pos/(?P<slug>[\w-]+)/confirm/$', menuposition_confirm, name='confirmpos'),

	url(r'^(?P<slug>[\w-]+)/total/$', menu_total_ingredients, name='total'),


]