from django.conf.urls import url
from django.contrib import admin

from recipes.api.views import (
	RecipeCreateAPIView,
	RecipeDeleteAPIView,
	RecipeDetailAPIView,
	RecipeListAPIView,
	RecipeUpdateAPIView
	)

urlpatterns = [
	url(r'^$', RecipeListAPIView.as_view(), name='list'),
    url(r'^create/$', RecipeCreateAPIView.as_view(),name='create'),
    url(r'^(?P<slug>[\w-]+)/$', RecipeDetailAPIView.as_view(), name='detail'),  #knowledge1
    url(r'^(?P<slug>[\w-]+)/edit/$', RecipeUpdateAPIView.as_view(), name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', RecipeDeleteAPIView.as_view(),name='delete'),
]