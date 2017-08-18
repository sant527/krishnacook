from rest_framework.pagination import(
	LimitOffsetPagination,
	PageNumberPagination
	)

class RecipeLimitOffsetPagination(LimitOffsetPagination):
	default_limit = 2
	max_limit = 3


class RecipePageNumberPagination(PageNumberPagination):
	page_size = 5

#this it most useful for pagination:

#max_limit how it is used.
#http://127.0.0.1:8000/api/ingredients/?limit=100&offset=2%22
#"next": "http://127.0.0.1:8000/api/ingredients/?limit=3&offset=3",


#default:
#http://127.0.0.1:8000/api/ingredients/
#"next": "http://127.0.0.1:8000/api/ingredients/?limit=2&offset=2",


