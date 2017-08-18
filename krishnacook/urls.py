"""krishnacook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import settings

from recipes.views import (
	recipe_list
	)
from accounts.views import (login_view, logout_view)

if settings.DEBUG:
	import debug_toolbar
	
urlpatterns = [
	#url(r'^register/', register_view, name='register'),
	url(r'^login/', login_view, name='login'),
	url(r'^logout/', logout_view, name='logout'),
	url(r'^admin/', admin.site.urls),
	url(r'^ingredients/', include("ingredients.urls", namespace='ingredients')),
	url(r'^typeofingredient/', include("typeofingredient.urls", namespace='typeofingredient')),
	url(r'^recipes/', include("recipes.urls", namespace='recipes')),
	url(r'^events/', include("menu.urls", namespace='menus')),
	url(r'^tags/', include("tags.urls", namespace='tags')),
	url(r'^mixedmeasurements/', include("recipe_ingredient_measurements.urls", namespace='mixedmeasurements')),
	url(r'^singlemeasurements/', include("single_measurements.urls", namespace='singlemeasurements')),


	
	url(r'^api/ingredients/', include("ingredients.api.urls", namespace='ingredients-api')),
	url(r'^api/recipes/', include("recipes.api.urls", namespace='recipes-api')),

	url(r'^$', recipe_list, name='recipelist'),
]


urlpatterns = [
	url(r'^__debug__/', include(debug_toolbar.urls)),
] + urlpatterns