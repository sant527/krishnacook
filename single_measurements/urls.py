from django.conf.urls import url
from django.contrib import admin
from .views import recipe_ingredient_measurements_list,recipe_ingredient_measurements_update,recipe_ingredient_measurements_delete,recipe_ingredient_measurements_confirm


urlpatterns = [
	url(r'^$', recipe_ingredient_measurements_list, name='list'),
	# url(r'^create/$', recipe_ingredient_measurements_create),
	# url(r'^(?P<slug>[\w-]+)/$', recipe_ingredient_measurements_detail, name='detail'),
	url(r'^(?P<slug>[\w-]+)/edit/$', recipe_ingredient_measurements_update, name='update'),
	url(r'^(?P<slug>[\w-]+)/delete/$', recipe_ingredient_measurements_delete, name='delete'),
	url(r'^(?P<slug>[\w-]+)/confirm/$', recipe_ingredient_measurements_confirm, name='confirm'),

]