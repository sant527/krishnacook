from django.conf.urls import url
from django.contrib import admin
from .views import ingredient_list,ingredient_update,ingredient_delete,ingredient_confirm,ingredient_formset_update,ingredient_formset_create,ingredient_density_formset_create,ingredients_densities_list


urlpatterns = [
	url(r'^$', ingredient_list, name='list'),
	url(r'^bulk/edit/$', ingredient_formset_update , name='formsetedit'),
	url(r'^bulk/create/$', ingredient_formset_create , name='formsetcreate'),
	url(r'^density/bulk/edit/$', ingredient_density_formset_create , name='formsetdensity'),
	url(r'^density/view/$', ingredients_densities_list , name='formsetdensity'),
	# url(r'^create/$', ingredient_create),
	# url(r'^(?P<slug>[\w-]+)/$', ingredient_detail, name='detail'),
	url(r'^(?P<slug>[\w-]+)/edit/$', ingredient_update, name='update'),
	url(r'^(?P<slug>[\w-]+)/delete/$', ingredient_delete, name='delete'),
	url(r'^(?P<slug>[\w-]+)/confirm/$', ingredient_confirm, name='confirm'),

]