from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from typeofingredient.models import TypeOfIngredient
from recipes.models import Recipe,RecipePosition
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Prefetch

# Create your models here.

class Ingredient(models.Model):
	KILOGRAM = 'kg'
	LITER = 'ltr'
	PIECES = 'pcs'
	MUNITS_CHOICES = (
		(KILOGRAM, 'Kilogram'),
		(LITER, 'Liter'),
		(PIECES, 'Pieces'),
	)

	name = models.CharField(max_length=200,unique=True,null=False)
	slug = models.SlugField(unique=True)
	munit = models.CharField(max_length=10,choices=MUNITS_CHOICES,default=KILOGRAM)
	rate = models.DecimalField(max_digits=19, decimal_places=2,validators=[MinValueValidator(0)],default=0)
	typeofingredient = models.ForeignKey(TypeOfIngredient, related_name='typeof_ingredient',null=True, blank=True,on_delete=models.PROTECT)
	density_kg_per_lt = models.DecimalField(max_digits=19, decimal_places=2,verbose_name='Density (kg/lt)',null=True,blank=True,validators=[MinValueValidator(0)])
	density_pcs_per_kg = models.DecimalField(max_digits=19, decimal_places=2,verbose_name='Density (pcs/kg)',null=True,blank=True,validators=[MinValueValidator(0)])
	density_pcs_per_lt = models.DecimalField(max_digits=19, decimal_places=2,verbose_name='Density (pcs/lt)',null=True,blank=True,validators=[MinValueValidator(0)])
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return '%s:%s (%s) - %s Rs/%s' % (self.id,self.name, self.munit, self.rate,  self.munit)

	def get_absolute_url_update(self):
		return reverse("ingredients:update", kwargs={"slug": self.slug})

	def get_absolute_url_confirm(self):
		return reverse("ingredients:confirm", kwargs={"slug": self.slug})

	def get_absolute_url_delete(self):
		return reverse("ingredients:delete", kwargs={"slug": self.slug})

	def cost_for_given_quantity(self,quantity):
		return quantity * self.rate



	def ingredient_quantity_for_the_menu(self,menu):
		instance = menu

		testingredient = self

		#getting all the list of recipes in the event
		test2 = instance.menu_positions.filter(menurecipe__recipe_positions__ingredient=testingredient).distinct()

		#going into each menuposition(i.e recipes)
		total_ingredient_quantity = 0
		for menuposition in test2:

			#getting the quantity of an ingredient in the recipe. (eg: tomato in the recipe. it can be used multiple times)
			quantity_ingredient_recipeposition = 0
			for recipepostion in menuposition.menurecipe.recipe_positions.filter(ingredient=testingredient).distinct().select_related('recipe','ingredient','mass_unit','volume_unit','pieces_unit'):
				quantity_ingredient_recipeposition = quantity_ingredient_recipeposition + recipepostion.get_cost_quantity()
				#print(quantity_ingredient_recipeposition)

			total_ingredient_quantity = total_ingredient_quantity + quantity_ingredient_recipeposition * menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()

		return {total_ingredient_quantity:self.munit}


	def ingredient_quantity_for_the_menu_recipe(self,menuposition):
		testingredient = self
		quantity_ingredient_recipeposition = 0
		for recipepostion in menuposition.menurecipe.recipe_positions.filter(ingredient=testingredient).distinct().select_related('recipe','ingredient','mass_unit','volume_unit','pieces_unit'):
			quantity_ingredient_recipeposition = quantity_ingredient_recipeposition + recipepostion.get_cost_quantity() * menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()
			#print(quantity_ingredient_recipeposition)
		return quantity_ingredient_recipeposition

	def ingredient_quantity_bulk_units_for_the_menu_recipe(self,menuposition):
		testingredient = self
		hare = []
		for recipepostion in menuposition.menurecipe.recipe_positions.filter(ingredient=testingredient).select_related('recipe','ingredient','mass_unit','volume_unit','pieces_unit'):
			data = dict()
			if recipepostion.mass_unit is not None and recipepostion.mass_quantity is not None and recipepostion.mass_quantity > 0 :
				data.update({recipepostion.mass_unit:recipepostion.mass_quantity})
			if recipepostion.volume_unit is not None and recipepostion.volume_quantity is not None and recipepostion.volume_quantity > 0 :
				data.update({recipepostion.volume_unit:recipepostion.volume_quantity})
			if recipepostion.pieces_unit is not None and recipepostion.pieces_quantity is not None and recipepostion.pieces_quantity > 0 :
				data.update({recipepostion.pieces_unit:recipepostion.pieces_quantity})
			hare.append(data)
		return hare

	def ingredient_quantity_bulk_units_for_the_menu_recipe_multiply_with_menuposition_factor(self,menuposition):
		testingredient = self
		hare = []
		for recipepostion in menuposition.menurecipe.recipe_positions.filter(ingredient=testingredient).select_related('recipe','ingredient','mass_unit','volume_unit','pieces_unit'):
			data = dict()
			if recipepostion.mass_unit is not None and recipepostion.mass_quantity is not None and recipepostion.mass_quantity > 0 :
				data.update({recipepostion.mass_unit:recipepostion.mass_quantity * menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
			if recipepostion.volume_unit is not None and recipepostion.volume_quantity is not None and recipepostion.volume_quantity > 0 :
				data.update({recipepostion.volume_unit:recipepostion.volume_quantity * menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
			if recipepostion.pieces_unit is not None and recipepostion.pieces_quantity is not None and recipepostion.pieces_quantity > 0 :
				data.update({recipepostion.pieces_unit:recipepostion.pieces_quantity * menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
			hare.append(data)
		return hare

	def ingredient_quantity_kg_ltr_pcs_for_the_menu_recipe_multiply_with_menuposition_factor(self,menuposition):
		testingredient = self
		hare = []
		for recipepostion in menuposition.menurecipe.recipe_positions.filter(ingredient=testingredient).select_related('recipe','ingredient','mass_unit','volume_unit','pieces_unit'):
			data = dict()
			if recipepostion.mass_unit is not None and recipepostion.mass_quantity is not None and recipepostion.mass_quantity > 0 :
				data.update({"kg":recipepostion.mass_quantity * recipepostion.mass_unit.quantity * menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
			if recipepostion.volume_unit is not None and recipepostion.volume_quantity is not None and recipepostion.volume_quantity > 0 :
				data.update({"ltr":recipepostion.volume_quantity  * recipepostion.volume_unit.quantity  * menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
			if recipepostion.pieces_unit is not None and recipepostion.pieces_quantity is not None and recipepostion.pieces_quantity > 0 :
				data.update({"pcs":recipepostion.pieces_quantity * recipepostion.pieces_unit.quantity* menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
			hare.append(data)
		return hare

	def get_mixed_density_custom_ingredient(self,menuposition):
		testingredient = self
		hare = []
		for recipepostion in menuposition.menurecipe.recipe_positions.filter(ingredient=testingredient).select_related('recipe','ingredient','mass_unit','volume_unit','pieces_unit'):
			data = recipepostion.get_cost_quantity_dict_custom_ingredient_mixed_density(menuposition.menu)
			hare.append(data)
		return hare
		
	def get_mixed_density_custom_ingredient_with_factor(self,menuposition):
		testingredient = self
		hare = []
		total_quantity = 0
		
		for recipepostion in menuposition.menurecipe.recipe_positions.filter(ingredient=testingredient).select_related('recipe','ingredient','mass_unit','volume_unit','pieces_unit'):
			factor = menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()
			data = recipepostion.cost_quantity_kg_ltr_pcs_units_dict_multiply_with_factor_custom_ingredient_mixed_density(factor,menuposition.menu)
			data.update({"count":self.get_the_number_of_actual_units_in_recepiposition(recipepostion)-1})
			total_quantity = total_quantity + data['quantity_factor']
			hare.append(data)
		
		finaldata = dict()
		finaldata.update({'data':hare,'total_quantity':total_quantity})
		#the total_quantity is the total of the same ingredients in the recipe.
		return finaldata

	def ingredient_quantity_for_the_menu_custom_ingredient(self,menu):
		instance = menu

		testingredient = self

		#getting all the list of recipes in the event
		test2 = instance.menu_positions.filter(menurecipe__recipe_positions__ingredient=testingredient).distinct()

		#going into each menuposition(i.e recipes)
		data = dict()
		total_quantity = 0
		for menuposition in test2:
			data = self.get_mixed_density_custom_ingredient_with_factor(menuposition)
			total_quantity = total_quantity + data['total_quantity']

		data.update({'default_rate':self.rate})
		data.update({'custom_rate':menu.menu_get_custom_ingredient_rate(self)})
	
		custom_rate = menu.menu_get_custom_ingredient_rate(self)
		if custom_rate == 0:
			mixed_rate = self.rate
			mixed_type = '(D)'
		else:
			mixed_rate = custom_rate
			mixed_type = '(C)'

		data.update({'mixed_rate':mixed_rate})
		data.update({'mixed_type':mixed_type})

		total_cost = total_quantity * mixed_rate
		data.update({'total_quantity':total_quantity})
		data.update({'total_cost':total_cost})

		return data







	def get_the_number_of_actual_units_in_recepiposition(self,recipepostion):
		i=0
		data=dict()
		if recipepostion.mass_unit is not None and recipepostion.mass_quantity is not None and recipepostion.mass_quantity > 0 :
			i=i+1
		if recipepostion.volume_unit is not None and recipepostion.volume_quantity is not None and recipepostion.volume_quantity > 0 :
			i=i+1
		if recipepostion.pieces_unit is not None and recipepostion.pieces_quantity is not None and recipepostion.pieces_quantity > 0 :
			i=i+1
		return i

	def ingredient_get_cost_quantity_data(self,menuposition):
		testingredient = self
		#length = len(self.ingredient_quantity_bulk_units_for_the_menu_recipe(menuposition))
		hare = []
		for recipepostion in menuposition.menurecipe.recipe_positions.filter(ingredient=testingredient).select_related('recipe','ingredient','mass_unit','volume_unit','pieces_unit'):
			data = dict()
			data.update({"unit":testingredient.munit,"cost":recipepostion.get_cost_quantity()})
			data.update({"count":self.get_the_number_of_actual_units_in_recepiposition(recipepostion) - 1})
			hare.append(data)

		final = {
				'count': 0,
				'hare': hare
				}
		return final

	def ingredient_get_cost_quantity_data_multiply_with_menuposition_factor(self,menuposition):
		testingredient = self
		#length = len(self.ingredient_quantity_bulk_units_for_the_menu_recipe(menuposition))
		hare = []
		for recipepostion in menuposition.menurecipe.recipe_positions.filter(ingredient=testingredient).select_related('recipe','ingredient','mass_unit','volume_unit','pieces_unit'):
			data = dict()
			data.update({"unit":testingredient.munit,"cost":recipepostion.get_cost_quantity() * menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
			data.update({"count":self.get_the_number_of_actual_units_in_recepiposition(recipepostion)-1})
			hare.append(data)

		final = {
				'count': 0,
				'hare': hare
				}
		return final
		
#*********************************************************************

	def ingredient_qty_rate_cost_default_ingredient(self,menu):
		ingredient_menu_recipes = self.ingredient_menu_recipes(menu)
		cost_quantity = 0
		listhare = set([])
		density_factor_exists_total = 0
		density_factor_exists = 0
		for menuposition in ingredient_menu_recipes:
			factor = menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()
			ingredient_recipepositions = self.ingredient_recipepositions(menuposition)
		
			for recipeposition in ingredient_recipepositions:
				recp_prop = recipeposition.dict_factor_density_cost_default_ing_recipeposition(factor)
				cost_quantity = cost_quantity + recp_prop['cost_quantity_factor']
				listhare.add(recp_prop['density_unit'])
				if recp_prop['density_unit'] != "--":
					density_factor_exists_total = density_factor_exists_total + 1
				if recp_prop['density_unit'] != "--":
					density_factor_exists = 1

		rate = self.rate
		cost = cost_quantity * rate
		data = dict()
		data.update({'cost_quantity':cost_quantity,'rate':rate,'cost':cost,'cost_unit':self.munit,'density_fact':listhare,'density_factor_exists_total':density_factor_exists_total,'density_factor_exists':density_factor_exists})
		return data

#*********************************************************************
#*********************************************************************
	def ingredient_qty_rate_cost_custom_ingredient(self,menu):
		ingredient_menu_recipes = self.ingredient_menu_recipes(menu)
		cost_quantity = 0
		listhare = set([])
		density_factor_exists_total = 0
		density_factor_exists = 0
		for menuposition in ingredient_menu_recipes:
			factor = menuposition.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()
			ingredient_recipepositions = self.ingredient_recipepositions(menuposition)		
			
		
			for recipeposition in ingredient_recipepositions:
				recp_prop = recipeposition.dict_factor_density_cost_custom_ing_recipeposition(menu,factor)
				cost_quantity = cost_quantity + recp_prop['cost_quantity_factor']
				rate_custom = recp_prop['rate']
				listhare.add(recp_prop['density_unit'])
				if recp_prop['density_unit'] != "--":
					density_factor_exists = density_factor_exists + 1
				if recp_prop['density_unit'] != "--":
					density_factor_exists = 1


		rate = rate_custom
		cost = cost_quantity * rate
		data = dict()
		data.update({'cost_quantity':cost_quantity,'rate':rate,'cost':cost,'cost_unit':self.munit,'density_fact':listhare,'density_factor_exists':density_factor_exists,'density_factor_exists':density_factor_exists})
		return data

#*********************************************************************
	def ingredient_qty_rate_cost_default_ingredient_all_recipes(self):
		cost_quantity = 0
		listhare = set([])
		density_factor_exists_total = 0
		density_factor_exists = 0
		factor = 1
		ingredient_recipepositions = RecipePosition.objects.filter(ingredient=self)

		for recipeposition in ingredient_recipepositions:
			recp_prop = recipeposition.dict_factor_density_cost_default_ing_recipeposition(factor)
			cost_quantity = cost_quantity + recp_prop['cost_quantity_factor']
			if recp_prop['density_unit'] != "--":
				density_factor_exists = 1
				listhare.add(recp_prop['density_unit'])
				break
			#listhare.add(recp_prop['density_unit'])
			if recp_prop['density_unit'] != "--":
				density_factor_exists_total = density_factor_exists_total + 1

		rate = self.rate
		cost = cost_quantity * rate
		data = dict()
		data.update({'cost_quantity':cost_quantity,'rate':rate,'cost':cost,'cost_unit':self.munit,'density_fact':listhare,'density_factor_exists_total':density_factor_exists_total,'density_factor_exists':density_factor_exists})
		return data

#*********************************************************************
#*********************************************************************

	def ingredient_menu_recipes(self,menu):
		instance = menu

		testingredient = self
		testingredient
		test2 = instance.menu_positions.filter(menurecipe__recipe_positions__ingredient=testingredient).distinct().select_related('menurecipe','menurecipe__mass_unit','menurecipe__volume_unit','menurecipe__pieces_unit')
		return test2

#*********************************************************************
#*********************************************************************

	def ingredient_recipepositions(self,menuposition):
		return menuposition.menurecipe.recipe_positions.filter(ingredient=self).select_related('recipe','ingredient','mass_unit','volume_unit','pieces_unit')

#*********************************************************************

	def ingredient_recipepositions_recipe(self,recipe):
		return recipe.recipe_positions.filter(ingredient=self)











		# Menu.objects.prefetch_related(
		# 	Prefetch("menu_positions",queryset=MenuPosition.objects.all()),
		# 	Prefetch("menu_positions__menurecipe__recipe_positions__ingredient",queryset=)






		# 	)


	class Meta:
		ordering = ["name"]



def create_slug_ingredient(instance, new_slug=None):
	slug = slugify(instance.name)
	if new_slug is not None:
		slug = new_slug
	qs = Ingredient.objects.filter(slug=slug).order_by("-id")
	exists = qs.exists()
	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug_ingredient(instance, new_slug=new_slug)
	return slug



def pre_save_ingredient_receiver(sender, instance, *args, **kwargs):
		num = Ingredient.objects.filter(pk=instance.pk).count()
		if num == 0 :
			print('INSERT !!')
			instance.slug = create_slug_ingredient(instance)
		else:
			print('UPDAT !!')
			if has_changed(instance,"name"):
				instance.slug = create_slug_ingredient(instance)

		if not instance.density_kg_per_lt:
			instance.density_kg_per_lt = 0
		if not instance.density_pcs_per_kg:
			instance.density_pcs_per_kg = 0
		if not instance.density_pcs_per_lt:
			instance.density_pcs_per_lt = 0



def has_changed(instance, field):
	if not instance.pk:
		return False
	old_value = instance.__class__._default_manager.filter(pk=instance.pk).values(field).get()[field]
	return not getattr(instance, field) == old_value			




		


pre_save.connect(pre_save_ingredient_receiver, sender=Ingredient)

"""
list = []

ingredient = Ingredient.objects.get(pk=39)
for recipepostion in Recipe.objects.get(id=11).recipe_positions.filter(ingredient=ingredient):
	data = dict()
	#print("******************************")
	#print(recipepostion.name)
	if recipepostion.mass_unit is not None and recipepostion.mass_quantity is not None and recipepostion.mass_quantity > 0 :
		data.update({recipepostion.mass_unit:recipepostion.mass_quantity})
	if recipepostion.volume_unit is not None and recipepostion.volume_quantity is not None and recipepostion.volume_quantity > 0 :
		#print(recipepostion.volume_quantity)
		data.update({recipepostion.volume_unit:recipepostion.volume_quantity})
		#print(data)
	if recipepostion.pieces_unit is not None and recipepostion.pieces_quantity is not None and recipepostion.pieces_quantity > 0 :
		data.update({recipepostion.pieces_unit:recipepostion.pieces_quantity})
	list.append(data)

"""