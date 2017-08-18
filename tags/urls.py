from django.conf.urls import url
from django.contrib import admin
from .views import tag_list,tag_update,tag_delete,tag_confirm


urlpatterns = [
	url(r'^$', tag_list, name='list'),
	# url(r'^create/$', tag_create),
	# url(r'^(?P<slug>[\w-]+)/$', tag_detail, name='detail'),
	url(r'^(?P<slug>[\w-]+)/edit/$', tag_update, name='update'),
	url(r'^(?P<slug>[\w-]+)/delete/$', tag_delete, name='delete'),
	url(r'^(?P<slug>[\w-]+)/confirm/$', tag_confirm, name='confirm'),

]