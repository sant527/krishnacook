from rest_framework.serializers import (ModelSerializer, 
	HyperlinkedIdentityField,
	SerializerMethodField,
	)



from ingredients.models import Ingredient


class IngredientCreateUpdateSerializer(ModelSerializer):
	class Meta:
		model = Ingredient
		fields = [
			'id',
			'name',
			'slug',
			'munit',
			'pack_quantity',
			'rate_per_pack',
			'rate_per_munit',
			'updated',
			'timestamp',
		]
		read_only_fields = ('id','slug','rate_per_munit','updated','timestamp') # use this if we dont want some fields to be updated/created by input


ingredient_detail_url = HyperlinkedIdentityField(
		view_name = 'ingredients-api:detail',
		lookup_field = 'slug'
		)

ingredient_detail_url_page = HyperlinkedIdentityField(
		view_name = 'ingredients:list'
		#lookup_field = 'slug'
		)



class IngredientListSerializer(ModelSerializer):
	# def get_absolute_url(self):
	#     return reverse("ingredients:detail", kwargs={"slug": self.slug})
	# similar to above one
	url = HyperlinkedIdentityField(
		view_name = 'ingredients-api:detail',
		lookup_field = 'slug'
		) #we can put this outside so that it can be used by all
	# delete_url = HyperlinkedIdentityField(
	# 	view_name='ingredients-api:delete',
	# 	lookup_field = 'slug'
	# 	)
	#url_page = ingredient_detail_url_page
	# image = SerializerMethodField()
	# markdown = SerializerMethodField()
	# user = SerializerMethodField()
	class Meta:
		model = Ingredient
		fields = [
			'url',
			'id',
			'name',
			'slug',
			'munit',
			'pack_quantity',
			'rate_per_pack',
			'rate_per_munit',
			'updated',
			'timestamp',
			#'user',   # knowledge 4 (even though logged in as abc we see the user id is default=1) Blog API with Django Rest Framework 10 of 33 - Associate User with View Methods-8-hJeWQgYTQ
			#'delete_url', (dont want to expose this)
			#'url_page',
		]

	# def get_user(self,obj):
	# 	return str(obj.user.username)

	# def get_markdown(self,obj):
	# 	obj.get_markdown()

	# def get_image(self,obj):
	# 	try:
	# 		image = obj.image.url
	# 	except:
	# 		image =  None
	# 	return image

class IngredientDetailSerializer(ModelSerializer):  #knowledge2
	#user = SerializerMethodField()
	url=ingredient_detail_url
	#image = SerializerMethodField()
	#markdown = SerializerMethodField()
	#url_page = ingredient_detail_url_page
	#when we declare something here we have to put it into the fileds here.
	class Meta:
		model = Ingredient
		fields = [
			'url',
			'id',
			'name',
			'slug',
			'munit',
			'pack_quantity',
			'rate_per_pack',
			'rate_per_munit',
			'updated',
			'timestamp',
			#w'url_page',
		]

	# def get_user(self,obj):
	# 	return str(obj.user.username)

	# def get_markdown(self,obj):
	# 	obj.get_markdown()

	# def get_image(self,obj):
	# 	try:
	# 		image = obj.image.url
	# 	except:
	# 		image =  None

	# 	return image