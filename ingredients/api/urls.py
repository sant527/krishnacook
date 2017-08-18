from django.conf.urls import url
from django.contrib import admin

from ingredients.api.views import (
	IngredientCreateAPIView,
	IngredientDeleteAPIView,
	IngredientDetailAPIView,
	IngredientListAPIView,
	IngredientUpdateAPIView
	)

urlpatterns = [
	url(r'^$', IngredientListAPIView.as_view(), name='list'),
    url(r'^create/$', IngredientCreateAPIView.as_view(),name='create'),
    url(r'^(?P<slug>[\w-]+)/$', IngredientDetailAPIView.as_view(), name='detail'),  #knowledge1
    url(r'^(?P<slug>[\w-]+)/edit/$', IngredientUpdateAPIView.as_view(), name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', IngredientDeleteAPIView.as_view(),name='delete'),
]