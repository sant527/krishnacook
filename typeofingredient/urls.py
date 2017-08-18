from django.conf.urls import url
from django.contrib import admin
from .views import typeofingredient_list,typeofingredient_update,typeofingredient_delete,typeofingredient_confirm


urlpatterns = [
	url(r'^$', typeofingredient_list, name='list'),
	# url(r'^create/$', typeofingredient_create),
	# url(r'^(?P<slug>[\w-]+)/$', typeofingredient_detail, name='detail'),
	url(r'^(?P<slug>[\w-]+)/edit/$', typeofingredient_update, name='update'),
	url(r'^(?P<slug>[\w-]+)/delete/$', typeofingredient_delete, name='delete'),
	url(r'^(?P<slug>[\w-]+)/confirm/$', typeofingredient_confirm, name='confirm'),

]