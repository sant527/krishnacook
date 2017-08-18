from django.db.models import Q

from rest_framework.pagination import(
	LimitOffsetPagination,
	PageNumberPagination
	)

from rest_framework.filters import(
	SearchFilter,
	OrderingFilter,
	)

from rest_framework.generics import (
	CreateAPIView,
	DestroyAPIView,
	ListAPIView,
	UpdateAPIView,
	RetrieveAPIView,
	RetrieveUpdateAPIView,
	RetrieveDestroyAPIView, #Blog API with Django Rest Framework 10 of 33 - Associate User with View Methods-8-hJeWQgYTQ 03:40 (use this to have preffilled and show the values in api view)
	)

from .serializers import (
	RecipeListSerializer,
	RecipeDetailSerializer,
	RecipeCreateUpdateSerializer
	) 

#Blog API with Django Rest Framework 11 of 33 - Custom Permissions--0c88d24qzM (for permissions we have to import the following)

from rest_framework.permissions import(
	AllowAny,
	IsAuthenticated,
	IsAdminUser,
	IsAuthenticatedOrReadOnly,
	)

from .pagination import(
	RecipeLimitOffsetPagination,
	RecipePageNumberPagination
	)

from .permissions import IsOwnerOrReadOnly
from recipes.models import Recipe

#knowledge1: order in alphabetical way



class RecipeCreateAPIView(CreateAPIView): #Lecture 9 Create Serializer and Create View 
# Using RecipeCreateSerializer to RecipeCreateUpdateSerializer
	queryset = Recipe.objects.all()
	serializer_class = RecipeCreateUpdateSerializer

	# Blog API with Django Rest Framework 10 of 33 - Associate User with View Methods-8-hJeWQgYTQ 02:22 (use perform_create to modify data )

	# def perform_create(self,serializer):
	# 	#serializer.save(user=self.request.user, title='mytitle') this will change the title and the user Blog API with Django Rest Framework 10 of 33 - Associate User with View Methods-8-hJeWQgYTQ 02:45
	# 	serializer.save(user=self.request.user)


class RecipeDetailAPIView(RetrieveAPIView):
	queryset = Recipe.objects.all()
	serializer_class = RecipeDetailSerializer
	lookup_field = 'slug'    #knowledge1
	#lookup_url_kawrg = "abc" #knowledge1

class RecipeUpdateAPIView(RetrieveUpdateAPIView): #Blog API with Django Rest Framework 10 of 33 - Associate User with View Methods-8-hJeWQgYTQ 03:40 (use RetrieveUpdateAPIView to have preffilled and show the values in api view)
	queryset = Recipe.objects.all()
	serializer_class = RecipeCreateUpdateSerializer
	lookup_field = 'slug' 
	# permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]

	# def perform_update(self,serializer): # #Blog API with Django Rest Framework 10 of 33 - Associate User with View Methods-8-hJeWQgYTQ 03:55 (perform_create is used for creating and perform update is used for updating)
	# 	serializer.save(user=self.request.user)

class RecipeDeleteAPIView(RetrieveDestroyAPIView):
	queryset = Recipe.objects.all()
	serializer_class = RecipeDetailSerializer
	lookup_field = 'slug'


class RecipeListAPIView(ListAPIView):
	#queryset = Recipe.objects.all()
	serializer_class = RecipeListSerializer
	filter_backends = [SearchFilter,OrderingFilter]
	search_fields = ['name','slug']

	#Builtint pagination
	#pagination_class = PageNumberPagination
	#pagination_class = LimitOffsetPagination
	#http://127.0.0.1:8000/api/recipes/?limit=2&offset=2

	#pagination_class = RecipeLimitOffsetPagination
	pagination_class = RecipePageNumberPagination




	#searching the non builtin way
	def get_queryset(self, *args, **kargs):
		queryset_list = Recipe.objects.all()
		query = self.request.GET.get("q")
		if query:
			queryset_list = queryset_list.filter(
				Q(name__icontains=query)|
				Q(slug__icontains=query)
				).distinct()
		return queryset_list

	#http://127.0.0.1:8000/api/recipes/?search=hare&ordering=title using built in


#Blog API with Django Rest Framework 13 of 33 - Pagination with Rest Framework-p4B8zFVRmHI: 06:39 default setting of classes of the rest_framework can be set up in the settings file like permissions etc.

"""
	knowledge1 : Blog API with Django Rest Framework 6 of 33 - Retrieve API View aka Detail View-dWZB_F32BDg.mp4

	00:02:34 to  00:04:12

	lookup_field = 'slug'
	lookup_url_kawrg = "abc"


	then 

	url(r'^(?P<abc>[\w-]+)/$', RecipeDetailAPIView.as_view(), name='detail'), -- work

"""

"""
knowledge: Blog API with Django Rest Framework 11 of 33 - Custom Permissions--0c88d24qzM

permissions:  not authorization.

if user is logged in then 


"""