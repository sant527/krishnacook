from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from recipes.models import Recipe, RecipePosition
from typeofingredient.models import TypeOfIngredient
from django.core.urlresolvers import reverse
from ingredients.models import Ingredient
import decimal
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
import arrow

class Menu(models.Model):
	name = models.CharField(max_length=200)
	slug = models.SlugField(unique=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.slug

	def get_url_menu_ingredient_custom_clear_all_values(self):
		return reverse("menus:customingredient_clear", kwargs={"slug": self.slug})

	def get_url_menu_ingredient_custom_sync_with_default(self):
		return reverse("menus:customingredient_sync", kwargs={"slug": self.slug})

	def get_absolute_url_update(self):
		return reverse("menus:update", kwargs={"slug": self.slug})

	def get_absolute_url_detail(self):
		return reverse("menus:default_detail", kwargs={"slug": self.slug})	

	def get_absolute_url_report(self):
		return reverse("menus:report", kwargs={"slug": self.slug})	

	def get_absolute_url_print(self):
		return reverse("menus:print", kwargs={"slug": self.slug})

	def get_absolute_url_detail_ingredient(self):
		return reverse("menus:detail_ingredient", kwargs={"slug": self.slug})

	def get_absolute_url_detail2(self):
		return reverse("menus:detail2", kwargs={"slug": self.slug})

	def get_absolute_url_confirm(self):
		return reverse("menus:confirm", kwargs={"slug": self.slug})

	def get_absolute_url_delete(self):
		return reverse("menus:delete", kwargs={"slug": self.slug})

	def get_absolute_url_menu_update_inline_bulk_recipes(self):
		return reverse("menus:updaterecipebulk", kwargs={"slug": self.slug})

	def get_absolute_url_customingredient(self):
		return reverse("menus:customingredient_list", kwargs={"slug": self.slug})	


	def get_absolute_url_default_ingredients(self):
		return reverse("menus:default_ingredients", kwargs={"slug": self.slug})	


	def get_absolute_url_default_recipes(self):
		return reverse("menus:default_recipes", kwargs={"slug": self.slug})	

	def menu_ingredient_default_inlineformset_bulk_edit(self):
		return reverse("menus:defaultingredient_bulkedit", kwargs={"slug": self.slug})



	def menu_ingredient_custom_inlineformset_bulk_edit(self):
		return reverse("menus:customingredient_bulkedit", kwargs={"slug": self.slug})

	def menu_ingredient_custom_recipe_report(self):
		return reverse("menus:custom_detail", kwargs={"slug": self.slug})	
	def menu_ingredient_custom_recipe_recipes(self):
		return reverse("menus:custom_recipes", kwargs={"slug": self.slug})	
	def menu_ingredient_custom_recipe_ingredients(self):
		return reverse("menus:custom_ingredients", kwargs={"slug": self.slug})		

	def get_number_of_recipes(self):
		return self.menu_positions.all().count()


	def menu_get_custom_ingredient_rate(self,ingredient):
		count = self.menu_positions_customingredients.all().filter(ingredient = ingredient).count()
		if count == 0:
			return 0;
		else:
			return self.menu_positions_customingredients.all().filter(ingredient = ingredient).first().rate

	def menu_get_custom_ingredient_density_dict(self,ingredient):
		data = dict()
		count = self.menu_positions_customingredients.all().filter(ingredient = ingredient).count()
		if count == 0:
			data.update({'density_kg_per_lt':0,'density_pcs_per_kg':0,'density_pcs_per_lt':0})
			return data
		else:
			density_kg_per_lt = self.menu_positions_customingredients.all().filter(ingredient = ingredient).first().density_kg_per_lt
			density_pcs_per_kg = self.menu_positions_customingredients.all().filter(ingredient = ingredient).first().density_pcs_per_kg
			density_pcs_per_lt = self.menu_positions_customingredients.all().filter(ingredient = ingredient).first().density_pcs_per_lt

			if density_kg_per_lt is None:
				data.update({'density_kg_per_lt':0})
			else:
				data.update({'density_kg_per_lt':density_kg_per_lt})

			if density_pcs_per_kg is None:
				data.update({'density_pcs_per_kg':0})
			else:
				data.update({'density_pcs_per_kg':density_pcs_per_kg})

			if density_pcs_per_lt is None:
				data.update({'density_pcs_per_lt':0})
			else:
				data.update({'density_pcs_per_lt':density_pcs_per_lt})
		return data

	def average_number_of_people(self):
		hare = self.menu_positions.all()
		if hare.exists():
			total_people = 0
			for recipe in hare:
				total_people = total_people + recipe.persons
			avgpeople = total_people/decimal.Decimal(hare.count())
			return avgpeople
		return 0

	def typeofingredients_from_menu(self):
		recipes = Recipe.objects.filter(menurecipe_positions__menu=self)
		ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')

		distinct_typeof_ingredient = TypeOfIngredient.objects.filter(typeof_ingredient__ingredient_recipeposition__recipe__in=recipes).distinct().order_by('name')

		return distinct_typeof_ingredient


	def ingredient_quantity_final_cost_based_on_type_of_ingredient(self):

		recipes = Recipe.objects.filter(menurecipe_positions__menu=self)
		
		ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')

		distinct_typeof_ingredient = TypeOfIngredient.objects.filter(typeof_ingredient__ingredient_recipeposition__recipe__in=recipes).distinct().order_by('name')

		hare = []

		for ty_of_ing in distinct_typeof_ingredient:
			ingredients_dictinct_ty_of_in = ingredients_dictinct.filter(typeofingredient=ty_of_ing)
			total_cost = 0
			total_volume = 0
			total_weight = 0
			total_pieces = 0
			data = dict()
			count = ingredients_dictinct_ty_of_in.count()
			for ingredient in ingredients_dictinct_ty_of_in:
				total_cost = total_cost + list(ingredient.ingredient_quantity_for_the_menu(self))[0] * ingredient.rate
				if list(ingredient.ingredient_quantity_for_the_menu(self).values())[0] == "ltr":
					total_volume = total_volume + list(ingredient.ingredient_quantity_for_the_menu(self))[0]
				if list(ingredient.ingredient_quantity_for_the_menu(self).values())[0] == "kg":
					total_weight = total_weight + list(ingredient.ingredient_quantity_for_the_menu(self))[0]

				if list(ingredient.ingredient_quantity_for_the_menu(self).values())[0] == "pcs":
					total_pieces = total_pieces + list(ingredient.ingredient_quantity_for_the_menu(self))[0]


			data.update({"type":ty_of_ing.name,"count":count,"cost":total_cost,"tvol":total_volume,"twt":total_weight,"tpcs":total_pieces})
			hare.append(data)

		ingredients_dictinct_ty_of_in = ingredients_dictinct.exclude(typeofingredient__isnull=False)

		total_cost = 0
		total_volume = 0
		total_weight = 0
		total_pieces = 0
		data = dict()
		count = ingredients_dictinct_ty_of_in.count()
		for ingredient in ingredients_dictinct_ty_of_in:
			total_cost = total_cost + list(ingredient.ingredient_quantity_for_the_menu(self))[0] * ingredient.rate
			if list(ingredient.ingredient_quantity_for_the_menu(self).values())[0] == "ltr":
				total_volume = total_volume + list(ingredient.ingredient_quantity_for_the_menu(self))[0]
			if list(ingredient.ingredient_quantity_for_the_menu(self).values())[0] == "kg":
				total_weight = total_weight + list(ingredient.ingredient_quantity_for_the_menu(self))[0]

			if list(ingredient.ingredient_quantity_for_the_menu(self).values())[0] == "pcs":
				total_pieces = total_pieces + list(ingredient.ingredient_quantity_for_the_menu(self))[0]


		data.update({"type":"None","count":count,"cost":total_cost,"tvol":total_volume,"twt":total_weight,"tpcs":total_pieces})
		hare.append(data)

		
		return hare

	def ingredient_quantity_final_cost_based_on_type_of_ingredient_custom_ingredient(self):

		recipes = Recipe.objects.filter(menurecipe_positions__menu=self)
		
		ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')

		distinct_typeof_ingredient = TypeOfIngredient.objects.filter(typeof_ingredient__ingredient_recipeposition__recipe__in=recipes).distinct().order_by('name')

		hare = []

		for ty_of_ing in distinct_typeof_ingredient:
			ingredients_dictinct_ty_of_in = ingredients_dictinct.filter(typeofingredient=ty_of_ing)
			total_cost = 0
			total_volume = 0
			total_weight = 0
			total_pieces = 0
			data = dict()
			count = ingredients_dictinct_ty_of_in.count()
			for ingredient in ingredients_dictinct_ty_of_in:
				total_cost = total_cost + ingredient.ingredient_quantity_for_the_menu_custom_ingredient(self)['total_cost']
				if ingredient.munit == "ltr":
					total_volume = total_volume + ingredient.ingredient_quantity_for_the_menu_custom_ingredient(self)['total_quantity']
				if ingredient.munit == "kg":
					total_weight = total_weight + ingredient.ingredient_quantity_for_the_menu_custom_ingredient(self)['total_quantity']
				if ingredient.munit == "pcs":
					total_pieces = total_pieces + ingredient.ingredient_quantity_for_the_menu_custom_ingredient(self)['total_quantity']
			data.update({"type":ty_of_ing.name,"count":count,"cost":total_cost,"tvol":total_volume,"twt":total_weight,"tpcs":total_pieces})
			hare.append(data)

		ingredients_dictinct_ty_of_in = ingredients_dictinct.exclude(typeofingredient__isnull=False)

		total_cost = 0
		total_volume = 0
		total_weight = 0
		total_pieces = 0
		data = dict()
		count = ingredients_dictinct_ty_of_in.count()
		for ingredient in ingredients_dictinct_ty_of_in:
			total_cost = total_cost + ingredient.ingredient_quantity_for_the_menu_custom_ingredient(self)['total_cost']
			if ingredient.munit == "ltr":
				total_volume = total_volume + ingredient.ingredient_quantity_for_the_menu_custom_ingredient(self)['total_quantity']
			if ingredient.munit == "kg":
				total_weight = total_weight + ingredient.ingredient_quantity_for_the_menu_custom_ingredient(self)['total_quantity']
			if ingredient.munit == "pcs":
				total_pieces = total_pieces + ingredient.ingredient_quantity_for_the_menu_custom_ingredient(self)['total_quantity']

		data.update({"type":"None","count":count,"cost":total_cost,"tvol":total_volume,"twt":total_weight,"tpcs":total_pieces})
		hare.append(data)

		
		return hare





	def ingredient_quantity_final_cost_for_the_menu(self):

		recipes = Recipe.objects.filter(menurecipe_positions__menu=self)
		ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')

		distinct_typeof_ingredient = TypeOfIngredient.objects.filter(typeof_ingredient__ingredient_recipeposition__recipe__in=recipes).distinct().order_by('name')

		total_cost = 0
		for ingredient in ingredients_dictinct:
			total_cost = total_cost + list(ingredient.ingredient_quantity_for_the_menu(self))[0] * ingredient.rate
		return total_cost

		#menu = Menu.objects.get(id=2)
		#recipes = Recipe.objects.filter(menurecipe_positions__menu=menu)
		#distinct_typeof_ingredient = TypeOfIngredient.objects.filter(typeof_ingredient__ingredient_recipeposition__recipe__in=recipes).distinct().order_by('name')

	def ingredient_quantity_final_cost_for_the_menu_custom_ingredient(self):

		recipes = Recipe.objects.filter(menurecipe_positions__menu=self)
		ingredients_dictinct = Ingredient.objects.filter(ingredient_recipeposition__recipe__in=recipes).distinct().order_by('typeofingredient')

		distinct_typeof_ingredient = TypeOfIngredient.objects.filter(typeof_ingredient__ingredient_recipeposition__recipe__in=recipes).distinct().order_by('name')

		total_cost = 0
		for ingredient in ingredients_dictinct:
			total_cost = total_cost + ingredient.ingredient_quantity_for_the_menu_custom_ingredient(self)['total_cost']
		return total_cost

		#menu = Menu.objects.get(id=2)
		#recipes = Recipe.objects.filter(menurecipe_positions__menu=menu)
		#distinct_typeof_ingredient = TypeOfIngredient.objects.filter(typeof_ingredient__ingredient_recipeposition__recipe__in=recipes).distinct().order_by('name')


#****************************** modified ************************

	def dict_default_prop_total_people_cost_menu(self):
		data=dict()
		hare = self.menu_positions.all()
		if hare.exists():
			total_people = 0
			factor_total_cost = 0
			total_cost_per_person = 0

			ltr_total = 0
			kg_total = 0
			pcs_total = 0

			for recipe in hare:
				prop = recipe.dict_default_factor_cost_prop_menurecipe()
				total_people = total_people + recipe.persons
				factor_total_cost = factor_total_cost + prop['fact_total_cost']
				total_cost_per_person = total_cost_per_person + prop['cost_per_person']

				if prop['consumption_unit'] == "ml":
					ltr_total = ltr_total + prop['factor_basic_qty']
				elif prop['consumption_unit'] == "g":
					kg_total = kg_total + prop['factor_basic_qty']
				elif prop['consumption_unit'] == "pcs":
					pcs_total = pcs_total + prop['factor_basic_qty']
				else:
					pass

			number_of_recipes = decimal.Decimal(hare.count())
			avgpeople = total_people/number_of_recipes
			avg_cost_per_person = factor_total_cost/avgpeople
			
			data.update({
						"total_people":total_people,
						"factor_total_cost":factor_total_cost,
						"total_cost_per_person":total_cost_per_person,
						"number_of_recipes":number_of_recipes,
						"avgpeople": avgpeople,
						"avg_cost_per_person": avg_cost_per_person,
						"ltr_total": ltr_total,
						"kg_total": kg_total,
						"pcs_total": pcs_total,
						})
			return data
		else:
			data.update({
						"total_people":0,
						"factor_total_cost":0,
						"total_cost_per_person":0,
						"number_of_recipes":0,
						"avgpeople": 0,
						"avg_cost_per_person": 0,
						"ltr_total": 0,
						"kg_total": 0,
						"pcs_total": 0,
						})
			return data


#****************************** modified ************************
#****************************** modified ************************

	def dict_custom_prop_total_people_cost_menu(self):
		data=dict()
		hare = self.menu_positions.all()
		if hare.exists():
			total_people = 0
			factor_total_cost = 0
			total_cost_per_person = 0
			
			ltr_total = 0
			kg_total = 0
			pcs_total = 0

			for recipe in hare:
				prop = recipe.dict_custom_factor_cost_prop_menurecipe()
				total_people = total_people + recipe.persons
				factor_total_cost = factor_total_cost + prop['fact_total_cost']
				total_cost_per_person = total_cost_per_person + prop['cost_per_person']
				if prop['consumption_unit'] == "ml":
					ltr_total = ltr_total + prop['factor_basic_qty']
				elif prop['consumption_unit'] == "g":
					kg_total = kg_total + prop['factor_basic_qty']
				elif prop['consumption_unit'] == "pcs":
					pcs_total = pcs_total + prop['factor_basic_qty']
				else:
					pass

			number_of_recipes = decimal.Decimal(hare.count())
			avgpeople = total_people/number_of_recipes
			avg_cost_per_person = factor_total_cost/avgpeople
			
			data.update({
						"total_people":total_people,
						"factor_total_cost":factor_total_cost,
						"total_cost_per_person":total_cost_per_person,
						"number_of_recipes":number_of_recipes,
						"avgpeople": avgpeople,
						"avg_cost_per_person": avg_cost_per_person,
						"ltr_total": ltr_total,
						"kg_total": kg_total,
						"pcs_total": pcs_total,
						})
			return data
		else:
			data.update({
						"total_people":0,
						"factor_total_cost":0,
						"total_cost_per_person":0,
						"number_of_recipes":0,
						"avgpeople": 0,
						"avg_cost_per_person": 0,
						"ltr_total": 0,
						"kg_total": 0,
						"pcs_total": 0,
						})
			return data


#****************************** modified ************************

	def average_number_of_people_dict_custom_ingredient(self):
		data=dict()
		hare = self.menu_positions.all()
		if hare.exists():
			total_people = 0
			total_cost = 0
			total_cost_individual = 0
			for recipe in hare:
				factor = recipe.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()
				total_people = total_people + recipe.persons
				total_cost = total_cost + recipe.menurecipe.get_cost_of_the_recipe_custom_price_ingredient_factor(factor,self)
				total_cost_individual = total_cost_individual + recipe.menurecipe.get_cost_of_the_recipe_custom_price_ingredient_factor_per_person(factor,self,recipe)
			avgpeople = total_people/decimal.Decimal(hare.count())
			count = decimal.Decimal(hare.count())
			avg_cost_per_person = total_cost/avgpeople
			total_cost_ind = total_cost_individual
			data.update({
						"totalp":total_people,
						"avgp":avgpeople,
						"countr":count,
						"total_cost":total_cost,
						"avg_cost_per_person": avg_cost_per_person,
						"total_cost_ind": total_cost_individual,
						})
			return data
		else:
			data.update({
						"totalp":"na",
						"avgp":"na",
						"countr":"na",
						"total_cost":"na",
						"avg_cost_per_person":"na",
						"total_cost_ind": "na",
						})
			return data

#**************************************************************************************8

	def total_cost(self):
		hare = self.menu_positions.all()
		if hare.exists():
			total_cost = 0
			for recipe in hare:
				total_cost = total_cost + recipe.get_totalcost_menuposition()
			return total_cost
		else:
			return 0;

	def cost_per_person_add_independent(self):
		hare = self.menu_positions.all()
		if hare.exists():
			total_cost = 0
			for recipe in hare:
				total_cost = total_cost + recipe.total_cost_per_person_kg_lt_pc_dict_single()["qty"]
			return total_cost
		else:
			return 0;

	def average_cost_per_person(self):
		hare = self.menu_positions.all()
		if hare.exists():
			a = (self.total_cost()/self.average_number_of_people())
			return a
		else:
			return 0;

	def total_quantity_liters(self):
		total_quantity = 0
		for recipeposition in self.menu_positions.all():
			total_quantity = total_quantity + recipeposition.recipe_get_total_volume_units_for_menu_decimal()
		return ('{:.2f} {}'.format(total_quantity,"lts"))

	def total_quantity_kilograms(self):
		total_quantity = 0
		for recipeposition in self.menu_positions.all():
			total_quantity = total_quantity + recipeposition.recipe_get_total_mass_units_for_menu_decimal()
		return ('{:.2f} {}'.format(total_quantity,"kgs"))

	def total_quantity_pieces(self):
		total_quantity = 0
		for recipeposition in self.menu_positions.all():
			total_quantity = total_quantity + recipeposition.recipe_get_total_pieces_units_for_menu_decimal()
		return ('{:.2f} {}'.format(total_quantity,"pcs"))


	def total_quantity_in_kg_lt_pcs_dict_all(self):
		data = dict()
		hare2 = self.menu_positions.all()
		ltr_total = 0
		kg_total = 0
		pcs_total = 0
		if hare2.exists():
			for hare in hare2:
				ltr_total = ltr_total + hare.total_quantity_in_kg_lt_pcs_dict()["ltr"]
				kg_total = kg_total + hare.total_quantity_in_kg_lt_pcs_dict()["kg"]
				pcs_total = pcs_total + hare.total_quantity_in_kg_lt_pcs_dict()["pcs"]

		data.update({"ltr":ltr_total,"kg":kg_total,"pcs":pcs_total})

		return data






	class Meta:
		ordering = ["-updated","-timestamp"]


def create_slug_menu(instance, new_slug=None):
	slug = slugify(instance.name)
	if new_slug is not None:
		slug = new_slug
	qs = Menu.objects.filter(slug=slug).order_by("-id")
	exists = qs.exists()
	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug_menu(instance, new_slug=new_slug)
	return slug


def pre_save_menu_receiver(sender, instance, *args, **kwargs):
		instance.slug = create_slug_menu(instance)

pre_save.connect(pre_save_menu_receiver, sender=Menu)





class MenuPosition(models.Model):
	KILOGRAM = 'kg'
	LITER = 'ltr'
	PIECES = 'pcs'
	MUNITS_CHOICES = (
		(KILOGRAM, 'Kilogram'),
		(LITER, 'Liter'),
		(PIECES, 'Pieces'),
	)

	name = models.CharField(max_length=200,blank=True,help_text="If left blank will be same as Recipe name Eg: Ekadasi alu fry")
	menu = models.ForeignKey(Menu,related_name='menu_positions', on_delete=models.CASCADE)
	menurecipe = models.ForeignKey(Recipe, related_name='menurecipe_positions',null=False, blank=False,on_delete=models.PROTECT,verbose_name='Menu Recipe')
	persons = models.PositiveSmallIntegerField(verbose_name='No of People',help_text="No of people for which the recipe will be made in this event")
	consumption_milli_liters = models.DecimalField(max_digits=19, decimal_places=5,null=True,blank=True,help_text="Consumption per Person In Milliters",validators=[MinValueValidator(1)])
	consumption_grams = models.DecimalField(max_digits=19, decimal_places=5,null=True,blank=True,help_text="Consumption per Person In Grams",validators=[MinValueValidator(1)])
	consumption_pieces = models.DecimalField(max_digits=19, decimal_places=5,null=True,blank=True,help_text="Consumption per Person In Pieces",validators=[MinValueValidator(0.1)])
	recipe_notes = models.CharField(max_length=200,blank=True)
	sequence_number = models.PositiveSmallIntegerField(default = 0,null=True,blank=True)
	title = models.CharField(max_length=200,blank=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)



	def get_absolute_url_update(self):
		return reverse("menus:updatepos", kwargs={"slug": self.id})

	def get_absolute_url_detail(self):
		return reverse("menus:detail", kwargs={"slug": self.menu.slug})	

	def get_absolute_url_confirm(self):
		return reverse("menus:confirmpos", kwargs={"slug": self.id})

	def get_absolute_url_delete(self):
		return reverse("menus:deletepos", kwargs={"slug": self.id})

	def get_totalcost_menuposition(self):
		return (self.cost_per_person() * self.persons)

	#***************************************************
	def dict_default_factor_cost_prop_menurecipe(self):
		if self.consumption_milli_liters is not None and self.consumption_milli_liters > 0:
			persons = self.persons
			factor_basic_qty = self.persons * self.consumption_milli_liters/1000
			factor_basic_unit = "ltr"
			Qty = self.menurecipe.list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe()
			basic_qty = Qty[1]['basic']['quantity']
			basic_unit = "ltr"
			factor = factor_basic_qty/basic_qty
			bulk_qty = Qty[1]['bulk']['quantity']
			bulk_unit = Qty[1]['bulk']['unit']
			fact_bulk_qty = bulk_qty * factor
			fact_bulk_unit = bulk_unit
			consumption = self.consumption_milli_liters
			consumption_unit = "ml"
			cost_per_basic_unit = self.menurecipe.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[1]['basic']['cost']
			fact_total_cost = factor_basic_qty * cost_per_basic_unit
			total_cost = fact_total_cost/factor #cost for the recipe actual formula
			cost_per_person = fact_total_cost/persons
			data = dict()
			data.update({
					"persons":persons,
					"factor_basic_qty":factor_basic_qty,
					"factor_basic_unit":factor_basic_unit,
					#"Qty":Qty,
					"basic_qty":basic_qty,
					"basic_unit":basic_unit,
					"factor":factor,
					"bulk_qty":bulk_qty,
					"bulk_unit":bulk_unit,
					"fact_bulk_qty":fact_bulk_qty,
					"fact_bulk_unit":fact_bulk_unit,
					"consumption":consumption,
					"consumption_unit":consumption_unit,
					"cost_per_basic_unit":cost_per_basic_unit,
					"fact_total_cost":fact_total_cost,
					"total_cost":total_cost,
					"cost_per_person":cost_per_person,
				})
			return data



		if self.consumption_grams is not None and self.consumption_grams > 0:
			persons = self.persons
			factor_basic_qty = self.persons * self.consumption_grams/1000
			factor_basic_unit = "kg"
			Qty = self.menurecipe.list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe()
			basic_qty = Qty[0]['basic']['quantity']
			basic_unit = "kg"
			factor = factor_basic_qty/basic_qty
			bulk_qty = Qty[0]['bulk']['quantity']
			bulk_unit = Qty[0]['bulk']['unit']
			fact_bulk_qty = bulk_qty * factor
			fact_bulk_unit = bulk_unit
			consumption = self.consumption_grams
			consumption_unit = "g"
			cost_per_basic_unit = self.menurecipe.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[0]['basic']['cost']
			fact_total_cost = factor_basic_qty * cost_per_basic_unit
			total_cost = fact_total_cost/factor #cost for the recipe actual formula
			cost_per_person = fact_total_cost/persons
			data = dict()
			data.update({
					"persons":persons,
					"factor_basic_qty":factor_basic_qty,
					"factor_basic_unit":factor_basic_unit,
					#"Qty":Qty,
					"basic_qty":basic_qty,
					"basic_unit":basic_unit,
					"factor":factor,
					"bulk_qty":bulk_qty,
					"bulk_unit":bulk_unit,
					"fact_bulk_qty":fact_bulk_qty,
					"fact_bulk_unit":fact_bulk_unit,
					"consumption":consumption,
					"consumption_unit":consumption_unit,
					"cost_per_basic_unit":cost_per_basic_unit,
					"fact_total_cost":fact_total_cost,
					"total_cost":total_cost,
					"cost_per_person":cost_per_person,
				})
			return data



		if self.consumption_pieces is not None and self.consumption_pieces > 0:
			persons = self.persons
			factor_basic_qty = self.persons * self.consumption_pieces/1000
			factor_basic_unit = "pcs"
			Qty = self.menurecipe.list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe()
			basic_qty = Qty[2]['basic']['quantity']
			basic_unit = "pcs"
			factor = factor_basic_qty/basic_qty
			bulk_qty = Qty[2]['bulk']['quantity']
			bulk_unit = Qty[2]['bulk']['unit']
			fact_bulk_qty = bulk_qty * factor
			fact_bulk_unit = bulk_unit
			consumption = self.consumption_pieces
			consumption_unit = "pcs"
			cost_per_basic_unit = self.menurecipe.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[2]['basic']['cost']
			fact_total_cost = factor_basic_qty * cost_per_basic_unit
			total_cost = fact_total_cost/factor #cost for the recipe actual formula
			cost_per_person = fact_total_cost/persons

			data = dict()
			data.update({
					"persons":persons,
					"factor_basic_qty":factor_basic_qty,
					"factor_basic_unit":factor_basic_unit,
					#"Qty":Qty,
					"basic_qty":basic_qty,
					"basic_unit":basic_unit,
					"factor":factor,
					"bulk_qty":bulk_qty,
					"bulk_unit":bulk_unit,
					"fact_bulk_qty":fact_bulk_qty,
					"fact_bulk_unit":fact_bulk_unit,
					"consumption":consumption,
					"consumption_unit":consumption_unit,
					"cost_per_basic_unit":cost_per_basic_unit,
					"fact_total_cost":fact_total_cost,
					"total_cost":total_cost,
					"cost_per_person":cost_per_person,
				})
			return data

		data = dict()
		data.update({
			"persons":0,
			"factor_basic_qty":0,
			"factor_basic_unit":"na",
			#"Qty":0,
			"basic_qty":0,
			"basic_unit":"na",
			"factor":0,
			"bulk_qty":0,
			"bulk_unit":"na",
			"fact_bulk_qty":0,
			"fact_bulk_unit":"na",
			"consumption":0,
			"consumption_unit":"na",
			"cost_per_basic_unit":0,
			"fact_total_cost":0,
			"total_cost":0,
			"cost_per_person":0,
			})
		return data
	#***********************************************************
	#***************************************************
	def dict_custom_factor_cost_prop_menurecipe(self):
		if self.consumption_milli_liters is not None and self.consumption_milli_liters > 0:
			persons = self.persons
			factor_basic_qty = self.persons * self.consumption_milli_liters/1000
			factor_basic_unit = "ltr"
			Qty = self.menurecipe.list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe()
			basic_qty = Qty[1]['basic']['quantity']
			basic_unit = "ltr"
			factor = factor_basic_qty/basic_qty
			bulk_qty = Qty[1]['bulk']['quantity']
			bulk_unit = Qty[1]['bulk']['unit']
			fact_bulk_qty = bulk_qty * factor
			fact_bulk_unit = bulk_unit
			consumption = self.consumption_milli_liters
			consumption_unit = "ml"
			cost_per_basic_unit = self.menurecipe.list_custom_cost_per_bulk_units_and_kg_ltr_pcs_recipe(self.menu)[1]['basic']['cost']
			fact_total_cost = factor_basic_qty * cost_per_basic_unit
			total_cost = fact_total_cost/factor #cost for the recipe actual formula
			cost_per_person = fact_total_cost/persons
			data = dict()
			data.update({
					"persons":persons,
					"factor_basic_qty":factor_basic_qty,
					"factor_basic_unit":factor_basic_unit,
					#"Qty":Qty,
					"basic_qty":basic_qty,
					"basic_unit":basic_unit,
					"factor":factor,
					"bulk_qty":bulk_qty,
					"bulk_unit":bulk_unit,
					"fact_bulk_qty":fact_bulk_qty,
					"fact_bulk_unit":fact_bulk_unit,
					"consumption":consumption,
					"consumption_unit":consumption_unit,
					"cost_per_basic_unit":cost_per_basic_unit,
					"fact_total_cost":fact_total_cost,
					"total_cost":total_cost,
					"cost_per_person":cost_per_person,
				})
			return data



		if self.consumption_grams is not None and self.consumption_grams > 0:
			persons = self.persons
			factor_basic_qty = self.persons * self.consumption_grams/1000
			factor_basic_unit = "kg"
			Qty = self.menurecipe.list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe()
			basic_qty = Qty[0]['basic']['quantity']
			basic_unit = "kg"
			factor = factor_basic_qty/basic_qty
			bulk_qty = Qty[0]['bulk']['quantity']
			bulk_unit = Qty[0]['bulk']['unit']
			fact_bulk_qty = bulk_qty * factor
			fact_bulk_unit = bulk_unit
			consumption = self.consumption_grams
			consumption_unit = "g"
			cost_per_basic_unit = self.menurecipe.list_custom_cost_per_bulk_units_and_kg_ltr_pcs_recipe(self.menu)[0]['basic']['cost']
			fact_total_cost = factor_basic_qty * cost_per_basic_unit
			total_cost = fact_total_cost/factor #cost for the recipe actual formula
			cost_per_person = fact_total_cost/persons
			data = dict()
			data.update({
					"persons":persons,
					"factor_basic_qty":factor_basic_qty,
					"factor_basic_unit":factor_basic_unit,
					#"Qty":Qty,
					"basic_qty":basic_qty,
					"basic_unit":basic_unit,
					"factor":factor,
					"bulk_qty":bulk_qty,
					"bulk_unit":bulk_unit,
					"fact_bulk_qty":fact_bulk_qty,
					"fact_bulk_unit":fact_bulk_unit,
					"consumption":consumption,
					"consumption_unit":consumption_unit,
					"cost_per_basic_unit":cost_per_basic_unit,
					"fact_total_cost":fact_total_cost,
					"total_cost":total_cost,
					"cost_per_person":cost_per_person,
				})
			return data



		if self.consumption_pieces is not None and self.consumption_pieces > 0:
			persons = self.persons
			factor_basic_qty = self.persons * self.consumption_pieces * 1
			factor_basic_unit = "pcs"
			Qty = self.menurecipe.list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe()
			basic_qty = Qty[2]['basic']['quantity']
			basic_unit = "pcs"
			factor = factor_basic_qty/basic_qty
			bulk_qty = Qty[2]['bulk']['quantity']
			bulk_unit = Qty[2]['bulk']['unit']
			fact_bulk_qty = bulk_qty * factor
			fact_bulk_unit = bulk_unit
			consumption = self.consumption_pieces
			consumption_unit = "pcs"
			cost_per_basic_unit = self.menurecipe.list_custom_cost_per_bulk_units_and_kg_ltr_pcs_recipe(self.menu)[2]['basic']['cost']
			fact_total_cost = factor_basic_qty * cost_per_basic_unit
			total_cost = fact_total_cost/factor #cost for the recipe actual formula
			cost_per_person = fact_total_cost/persons

			data = dict()
			data.update({
					"persons":persons,
					"factor_basic_qty":factor_basic_qty,
					"factor_basic_unit":factor_basic_unit,
					#"Qty":Qty,
					"basic_qty":basic_qty,
					"basic_unit":basic_unit,
					"factor":factor,
					"bulk_qty":bulk_qty,
					"bulk_unit":bulk_unit,
					"fact_bulk_qty":fact_bulk_qty,
					"fact_bulk_unit":fact_bulk_unit,
					"consumption":consumption,
					"consumption_unit":consumption_unit,
					"cost_per_basic_unit":cost_per_basic_unit,
					"fact_total_cost":fact_total_cost,
					"total_cost":total_cost,
					"cost_per_person":cost_per_person,
				})
			return data

		data = dict()
		data.update({
			"persons":0,
			"factor_basic_qty":0,
			"factor_basic_unit":"na",
			#"Qty":0,
			"basic_qty":0,
			"basic_unit":"na",
			"factor":0,
			"bulk_qty":0,
			"bulk_unit":"na",
			"fact_bulk_qty":0,
			"fact_bulk_unit":"na",
			"consumption":0,
			"consumption_unit":"na",
			"cost_per_basic_unit":0,
			"fact_total_cost":0,
			"total_cost":0,
			"cost_per_person":0,
			})
		return data
	#***********************************************************

	def const_cost_per_person_menuposition(self):
		factor = self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()
		total_cost = self.menurecipe.dict_total_and_fact_cost_recipe()['total_cost']
		persons = self.persons
		cost_per_person = (total_cost * factor)/persons
		return cost_per_person


	def const_cost_per_person_custom_rates_menuposition(self):
		factor = self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()
		total_cost = self.menurecipe.dict_total_and_fact_cost_custom_ing_recipe(self.menu)['total_cost']
		persons = self.persons
		cost_per_person = (total_cost * factor)/persons
		return cost_per_person

	# done ************** returns the factor ************************
	def menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs(self):
		if self.consumption_milli_liters and self.menurecipe.get_Volume_quantity()>0 :
			return self.get_total_units_kg_lt_pieces()/self.menurecipe.list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe()[1]['basic']['quantity']
		if self.consumption_grams and self.consumption_grams > 0 and self.menurecipe.get_Mass_quantity()>0:
			return self.get_total_units_kg_lt_pieces()/self.menurecipe.list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe()[0]['basic']['quantity']
		if self.consumption_pieces and self.menurecipe.get_Pieces_quantity()>0:
			return self.get_total_units_kg_lt_pieces()/self.menurecipe.self.menurecipe.list_total_factor_qty_unit_bulk_and_kg_ltr_pcs_recipe()[2]['basic']['quantity']
		return 0

	# done *********** returns the total quantity ****************************

	def get_total_units_kg_lt_pieces(self):
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			return (self.persons * self.consumption_milli_liters/1000)
		if self.consumption_grams and self.consumption_grams > 0:
			return (self.persons * self.consumption_grams/1000)
		if self.consumption_pieces and self.consumption_pieces > 0:
			return (self.persons * self.consumption_pieces)
		return 0


	# done *********** returns cons and units ****************************
	def get_person_consumption_dict_single(self):
		data=dict()
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			data.update({"unit": "ml" ,"qty":self.consumption_milli_liters})
			return data
		if self.consumption_grams and self.consumption_grams > 0:			
			data.update({"unit": "g" ,"qty":self.consumption_grams})
			return data
		if self.consumption_pieces and self.consumption_pieces > 0:
			data.update({"unit": "pcs" ,"qty":self.consumption_pieces})
			return data
		data.update({"unit": "na" ,"qty":0})
		return data

	# done *********************************************

	def cost_per_recipe_for_the_consumption_unit_class(self):
		data=dict()
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			data.update({"unit":"ltr","cost":self.menurecipe.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[1]['basic']['cost']})
			return data
		if self.consumption_grams and self.consumption_grams > 0:
			data.update({"unit":"kg","cost":self.menurecipe.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[0]['basic']['cost']})
			return data
		if self.consumption_pieces and self.consumption_pieces > 0:
			data.update({"unit":"pcs","cost":self.menurecipe.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()[2]['basic']['cost']})
			return data
		data.update({"unit":"na","cost":"na"})
		return data

	#*******************************************************8

	def total_cost_for_total_quantity_kg_lt_pc_dict_single(self):
		cost = self.menurecipe.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()
		data=dict()
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			data.update({"unit": "ltr" ,"qty":self.persons * self.consumption_milli_liters/1000 * cost[1]['basic']['cost']})
			return data
		if self.consumption_grams and self.consumption_grams > 0:			
			data.update({"unit": "g" ,"qty":self.persons * self.consumption_grams/1000 * cost[0]['basic']['cost']})
			return data
		if self.consumption_pieces and self.consumption_pieces > 0:
			data.update({"unit": "pcs" ,"qty":self.persons * self.consumption_pieces * cost[2]['basic']['cost']})
			return data
		data.update({"unit": "na" ,"qty":0})
		return data

	#*********************************************************
	def total_cost_per_person_kg_lt_pc_dict_single(self):
		cost = self.menurecipe.list_cost_per_bulk_units_and_kg_ltr_pcs_recipe()
		data=dict()
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			data.update({"unit": "ltr" ,"qty":self.consumption_milli_liters/1000 * cost[1]['basic']['cost']})
			return data
		if self.consumption_grams and self.consumption_grams > 0:			
			data.update({"unit": "g" ,"qty":self.consumption_grams/1000 * cost[0]['basic']['cost']})
			return data
		if self.consumption_pieces and self.consumption_pieces > 0:
			data.update({"unit": "pcs" ,"qty":self.consumption_pieces * cost[2]['basic']['cost']})
			return data
		data.update({"unit": "na" ,"qty":0})
		return data

	#****************************************************


	def total_quantity_in_kg_lt_pcs_dict_single(self):
		data=dict()
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			data.update({"unit": "ltr" ,"qty":self.persons * self.consumption_milli_liters/1000})
			data.update({"bulkunit": self.menurecipe.volume_unit.slug ,"bulkqty":(self.persons * self.consumption_milli_liters/1000)/self.menurecipe.volume_unit.quantity})
			return data
		if self.consumption_grams and self.consumption_grams > 0:			
			data.update({"unit": "kg" ,"qty":self.persons * self.consumption_grams/1000})
			data.update({"bulkunit": self.menurecipe.mass_unit.slug ,"bulkqty":(self.persons * self.consumption_grams/1000)/self.menurecipe.mass_unit.quantity})
			return data
		if self.consumption_pieces and self.consumption_pieces > 0:
			data.update({"unit": "pcs" ,"qty":self.persons * self.consumption_pieces})
			data.update({"bulkunit": self.menurecipe.pieces_unit.slug ,"bulkqty":(self.persons * self.consumption_pieces)/self.menurecipe.pieces_unit.quantity})
			return data
		data.update({"unit": "na" ,"qty":0,"bulkunit":"na","bulkqty":0})
		return 

	#**********************************************************************

	#it can happen that we change the yield from mass to volume units but the per person units are not changed then it will lead to inconsistency. presently we want to keep things flexible.so we will check the units.
	def checking_units_matching(self):

		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			if self.menurecipe.volume_unit and self.menurecipe.volume_quantity > 0:
				return "Match ml"
			else:
				return "Not Match ml"
		if self.consumption_grams and self.consumption_grams > 0:
			if self.menurecipe.mass_unit and self.menurecipe.mass_quantity > 0:
				return "Match g"
			else:
				return "Not Match g"
		if self.consumption_pieces and self.consumption_pieces > 0:
			if self.menurecipe.pieces_unit and self.menurecipe.pieces_quantity > 0:
				return "Match pcs"
			else:
				return "Not Match pcs"
		return "NULL"




	def get_person_consumption_dict(self):
		data=dict()
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			data.update({"ml":self.consumption_milli_liters})
		else:
			data.update({"ml":0})
		if self.consumption_grams and self.consumption_grams > 0:			
			data.update({"g":self.consumption_grams})
		else:
			data.update({"g":0})
		if self.consumption_pieces and self.consumption_pieces > 0:
			data.update({"pcs":self.consumption_pieces})
		else:
			data.update({"pcs":0})
		return data


	def total_quantity_in_kg_lt_pcs_dict(self):
		data=dict()
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			data.update({"ltr":self.persons * self.consumption_milli_liters/1000})
		else:
			data.update({"ltr":0})
		if self.consumption_grams and self.consumption_grams > 0:			
			data.update({"kg":self.persons * self.consumption_grams/1000})
		else:
			data.update({"kg":0})
		if self.consumption_pieces and self.consumption_pieces > 0:
			data.update({"pcs":self.persons * self.consumption_pieces})
		else:
			data.update({"pcs":0})
		return data


	def total_cost_for_total_quantity_kg_lt_pc_dict(self):
		cost = self.menurecipe.get_cost_of_the_recipe_per_kg_lt_pcs_unit_dict()
		data=dict()
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			data.update({"ltr":self.persons * self.consumption_milli_liters/1000 * cost["ltr"]})
		else:
			data.update({"ltr":0})
		if self.consumption_grams and self.consumption_grams > 0:			
			data.update({"kg":self.persons * self.consumption_grams/1000 * cost["kg"]})
		else:
			data.update({"kg":0})
		if self.consumption_pieces and self.consumption_pieces > 0:
			data.update({"pcs":self.persons * self.consumption_pieces * cost["pcs"]})
		else:
			data.update({"pcs":0})
		return data




	def total_cost_per_person_kg_lt_pc_dict(self):
		cost = self.menurecipe.get_cost_of_the_recipe_per_kg_lt_pcs_unit_dict()
		data=dict()
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			data.update({"ltr":self.consumption_milli_liters/1000 * cost["ltr"]})
		else:
			data.update({"ltr":0})
		if self.consumption_grams and self.consumption_grams > 0:			
			data.update({"kg":self.consumption_grams/1000 * cost["kg"]})
		else:
			data.update({"kg":0})
		if self.consumption_pieces and self.consumption_pieces > 0:
			data.update({"pcs":self.consumption_pieces * cost["pcs"]})
		else:
			data.update({"pcs":0})
		return data

	




	def get_only_units_kg_lt_pieces(self):
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			return ("ltr")
		if self.consumption_grams and self.consumption_grams > 0:
			return ("grams")
		if self.consumption_pieces and self.consumption_pieces > 0:
			return ("pcs")
		return 0



	def cost_per_recipe_for_the_consumption_unit_class_custom_ingredient_mixed(self):
		total_cost_custom_prices = self.menurecipe.get_cost_of_the_recipe_custom_price_ingredient(self.menu)
		data=dict()
		if self.consumption_milli_liters is not None and self.consumption_milli_liters > 0:
			data.update({"unit":"ltr","cost":(total_cost_custom_prices/(self.menurecipe.volume_quantity * self.menurecipe.volume_unit.quantity))})
			return data
		if self.consumption_grams is not None and self.consumption_grams > 0:
			data.update({"unit":"kg","cost":(total_cost_custom_prices/(self.menurecipe.mass_quantity * self.menurecipe.mass_unit.quantity))})
			return data
		if self.consumption_pieces is not None and self.consumption_pieces > 0:
			data.update({"unit":"pcs","cost":(total_cost_custom_prices/(self.menurecipe.pieces_quantity * self.menurecipe.pieces_unit.quantity))})
			return data
		data.update({"unit":"na","cost":"na"})
		return data

	def cost_per_person(self):
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			return (self.menurecipe.get_cost_of_the_recipe_per_unit_volume() * self.consumption_milli_liters/1000)
		if self.consumption_grams and self.consumption_grams > 0:
			return (self.menurecipe.get_cost_of_the_recipe_per_unit_mass() * self.consumption_grams/1000)
		if self.consumption_pieces and self.consumption_pieces > 0:
			return (self.menurecipe.get_cost_of_the_recipe_per_unit_pieces() * self.consumption_pieces)
		return 0

	def menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs(self):
		if self.consumption_milli_liters and self.menurecipe.get_Volume_quantity()>0 :
			return self.get_total_units_kg_lt_pieces()/self.menurecipe.get_Volume_quantity()
		if self.consumption_grams and self.consumption_grams > 0 and self.menurecipe.get_Mass_quantity()>0:
			return self.get_total_units_kg_lt_pieces()/self.menurecipe.get_Mass_quantity()
		if self.consumption_pieces and self.menurecipe.get_Pieces_quantity()>0:
			return self.get_total_units_kg_lt_pieces()/self.menurecipe.get_Pieces_quantity()
		return 0

	def menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs_dict(self):
		data = dict()
		if self.consumption_milli_liters and self.menurecipe.get_Volume_quantity() > 0:
			data.update({"ltr":self.get_total_units_kg_lt_pieces()/self.menurecipe.get_Volume_quantity()})
		else:
			data.update({"ltr":0})
		if self.consumption_grams and self.consumption_grams > 0 and self.menurecipe.get_Mass_quantity()>0:
			data.update({"kg":self.get_total_units_kg_lt_pieces()/self.menurecipe.get_Mass_quantity()})
		else:
			data.update({"kg":0})
		if self.consumption_pieces and self.menurecipe.get_Pieces_quantity()>0:
			data.update({"pcs":self.get_total_units_kg_lt_pieces()/self.menurecipe.get_Pieces_quantity()})
		else:
			data.update({"pcs":0})
		return data

	def menurecipe_which_units(self):
		if self.consumption_milli_liters and self.consumption_milli_liters > 0:
			return self.menurecipe.get_Volume_quantity()
		if self.consumption_grams and self.consumption_grams > 0:
			return self.menurecipe.get_Mass_quantity()
		if self.consumption_pieces and self.consumption_pieces > 0:
			return self.menurecipe.get_Pieces_quantity()
		return 0
		

	def recipe_get_total_volume_bulk_units_for_menu(self):
		if self.menurecipe.volume_unit and self.menurecipe.volume_quantity > 0 : 
			return ('{:.2f} {}'.format(self.menurecipe.volume_quantity * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs(),self.menurecipe.volume_unit.slug))
		return 0
	
	def recipe_get_total_mass_bulk_units_for_menu(self):
		if self.menurecipe.mass_unit and self.menurecipe.mass_quantity > 0:
			return ('{:.2f} {}'.format(self.menurecipe.mass_quantity * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs(),self.menurecipe.mass_unit.slug))
		return 0
	

	def recipe_get_total_pieces_bulk_units_for_menu(self):
		if self.menurecipe.pieces_unit and self.menurecipe.pieces_quantity > 0:
			return ('{:.2f} {}'.format(self.menurecipe.pieces_quantity * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs(),self.menurecipe.pieces_unit.slug))
		return 0

	def recipe_get_total_bulk_units_for_menu_dict(self):
		data = dict()
		if self.menurecipe.volume_unit and self.menurecipe.volume_quantity > 0 : 
			data.update({self.menurecipe.volume_unit.slug:self.menurecipe.volume_quantity * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
		else:
			data.update({"ltr":0})
		if self.menurecipe.mass_unit and self.menurecipe.mass_quantity > 0:
			data.update({self.menurecipe.mass_unit.slug:self.menurecipe.mass_quantity * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
		else:
			data.update({"kg":0})
		if self.menurecipe.pieces_unit and self.menurecipe.pieces_quantity > 0:
			data.update({self.menurecipe.pieces_unit.slug:self.menurecipe.pieces_quantity * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
		else:
			data.update({"pcs":0})
		return data

	def recipe_get_total_kg_lt_pcs_units_for_menu_dict(self):
		data = dict()
		if self.menurecipe.volume_unit and self.menurecipe.volume_quantity > 0 : 
			data.update({"ltr":self.menurecipe.volume_quantity * self.menurecipe.volume_unit.quantity * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
		else:
			data.update({"ltr":0})
		if self.menurecipe.mass_unit and self.menurecipe.mass_quantity > 0:
			data.update({"kg":self.menurecipe.mass_quantity * self.menurecipe.mass_unit.quantity * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
		else:
			data.update({"kg":0})
		if self.menurecipe.pieces_unit and self.menurecipe.pieces_quantity > 0:
			data.update({"pcs":self.menurecipe.pieces_quantity * self.menurecipe.pieces_unit.quantity * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()})
		else:
			data.update({"pcs":0})
		return data




	def recipe_get_total_volume_units_for_menu_formatted(self):
		if self.menurecipe.volume_unit and self.menurecipe.volume_quantity > 0 : 
			return ('{:.2f} {}'.format(self.menurecipe.get_Volume_quantity() * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs(),'ltr'))
		return 0
	
	def recipe_get_total_mass_units_for_menu_formatted(self):
		if self.menurecipe.mass_unit and self.menurecipe.mass_quantity > 0:
			return ('{:.2f} {}'.format(self.menurecipe.get_Mass_quantity() * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs(),'kg'))
		return 0
	

	def recipe_get_total_pieces_units_for_menu_formatted(self):
		if self.menurecipe.pieces_unit and self.menurecipe.pieces_quantity > 0:
			return ('{:.2f} {}'.format(self.menurecipe.get_Pieces_quantity() * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs(),'pcs'))
		return 0


	def convert_ml_g_pcs_to_ltr_kg_pcs(self):		
		data = dict()
		data.update({"ml-ltr":"1/1000"})
		data.update({"g-kg":"1/1000"})
		data.update({"pcs":"1"})
		return data

	



	######## without formating

	def recipe_get_total_volume_units_for_menu_decimal(self):
		if self.menurecipe.volume_unit and self.menurecipe.volume_quantity > 0 : 
			return self.menurecipe.get_Volume_quantity() * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()
		return 0
	
	def recipe_get_total_mass_units_for_menu_decimal(self):
		if self.menurecipe.mass_unit and self.menurecipe.mass_quantity > 0:
			return self.menurecipe.get_Mass_quantity() * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()
		return 0
	

	def recipe_get_total_pieces_units_for_menu_decimal(self):
		if self.menurecipe.pieces_unit and self.menurecipe.pieces_quantity > 0:
			return self.menurecipe.get_Pieces_quantity() * self.menurecipe_factor_of_recipe_quantity_wrt_lt_kg_pcs()
		return 0


	class Meta:
		ordering = ["-updated"]


	def __str__(self):
		 return '%s::%s' % (self.menurecipe.name,self.menu.name)

def pre_save_menuposition_receiver(sender, instance, *args, **kwargs):
	if instance.name == "":
		instance.name = instance.menurecipe.name

pre_save.connect(pre_save_menuposition_receiver, sender=MenuPosition)







class IngredientCustom(models.Model):
	menu = models.ForeignKey(Menu,related_name='menu_positions_customingredients', on_delete=models.CASCADE, null=False,blank=False)
	ingredient = models.ForeignKey(Ingredient,related_name='ingredient_positions_customingredients', null=False,blank=False,on_delete=models.PROTECT)
	rate = models.DecimalField(max_digits=19, decimal_places=2,validators=[MinValueValidator(0)],default=0)
	density_kg_per_lt = models.DecimalField(max_digits=19, decimal_places=2,verbose_name='Density (kg/lt)',null=True,blank=True,validators=[MinValueValidator(0)])
	density_pcs_per_kg = models.DecimalField(max_digits=19, decimal_places=2,verbose_name='Density (pcs/kg)',null=True,blank=True,validators=[MinValueValidator(0)])
	density_pcs_per_lt = models.DecimalField(max_digits=19, decimal_places=2,verbose_name='Density (pcs/lt)',null=True,blank=True,validators=[MinValueValidator(0)])
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)


	def __str__(self):
		return '%s::%s' % (self.menu.name, self.ingredient)

	class Meta:
		ordering=['ingredient']
















"""


test = MenuPosition.objects.select_related('menurecipe').filter(menu__name="evening prasad")
multi = test[0].quantity
hare = test[0].menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * multi)

multi = 
hare = MenuPosition.objects.select_related('menurecipe').filter(menu__name="evening prasad")[0].menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * test[0].quantity)


ingredients[0].total_quantity
ingredients = MenuPosition.objects.select_related('menurecipe').filter(menu__name="evening prasad")[0].menurecipe.recipe_positions.annotate(total_quantity=F('quantity') * test[0].quantity)

from menu.models import Menu, MenuPosition
from recipes.models import Recipe, RecipePosition
from typeofingredient.models import TypeOfIngredient

menu1 = Menu.objects.get(name="evening special")
menupostions1 = MenuPosition.menu_positions.all()



test = MenuPosition.objects.filter(menu__name="evening special").first()
#print(test.menurecipe.name)
gaura = RecipePosition.objects.filter(recipe__name=test.menurecipe.name).first().ingredientname
#print(gaura)




MenuPosition.objects.count()

MenuPosition.objects.filter(menu__name='evening special').count()


class Group(models.Model):
	name = models.CharField(max_length=100)

class Student(models.Model):
	name = models.CharField(max_length=100)
	group = models.ForeignKey(Group)


group1 = Group.objects.create(name='Group 1')
group1 = Group.objects.create(name='Group 2')
Student.objects.create(name='stud1', group=group1)
Student.objects.create(name='stud2', group=group1)
Student.objects.create(name='stud3', group=group1)
Student.objects.create(name='stud1', group=group2)


Intuitive way:
get all groups having stud1


group_ids = Student.objects.filter(name='stud1').values_list('group', flat=True)
groups = Group.objects.filter(id__in=group_ids)

Less obvious way:
Group.objects.filter(student__name='stud1')


Get the groups with name Group1 which contain students named stud1


Intuitive way:
group_ids = Student.objects.filter(name='stud1', group__name='Group1').values_list('group', flat=True)
groups = Group.objects.filter(id__in=group_ids)


Less obvious way:
groups = Group.objects.filter(name='Group1', student__name='stud1')


MyModel has a ForeignKey to MyRelatedModel

myobj = MyModel.objects.get(pk=1)
print myobj.myrelatedmodel.name

this hits the database two separate times - once to get the MyModel object, and once to get the related MyRelatedModel object. 

myobj = MyModel.objects.select_related.get(pk=1)

This way Django does a JOIN in the database call, and caches the related object in a hidden attribute of myobj. Printing myobj.__dict__ will show this:

{'_myrelatedmodel_cache': [MyRelatedModel: obj],
 'name': 'My name'}


---reverse

However, what's not obvious is how to do the same for reverse relationships. In other words, this:

myrelatedobj = MyRelatedObject.objects.get(pk=1)
print myrelatedobj.mymodel_set.all() 



<ul>
{% for obj in myobjects %}
	<li>{{ myobj.name }}</li>
	<ul>
		 {% for relobj in myobj.backwardsrelationship_set.all %}
		 <li>{{ relobj.name }}</li>
		 {% endfor %}
	</ul>
{% endfor %}
</ul>

Here you'll always get two separate db calls, and adding select_related() anywhere won't help at all. Now one extra db call isn't that significant, but consider this in a template:



c = Course.objects.get(id=1)
sessions = Session.objects.filter(course__id=c.id) # First way, forward lookup.
sessions = c.session_set.all() # Second way using the reverse lookup session_set added to Course object.

You'll also want to familiarize with annotate() and aggregate(), these allow you you to calculate fields and order/filter on the results. For example, Count, Sum, Avg, Min, Max, etc.

courses_with_at_least_five_students = Course.objects.annotate(
	num_students=Count('coursesignup_set__all')
).order_by(
	'-num_students'
).filter(
	num_students__gte=5
)


course_earliest_session_within_last_240_days_with_avg_teacher_rating_below_4 = Course.objects.annotate(
	min_session_date_from = Min('session_set__all')
).annotate(
	avg_teacher_rating = Avg('teacherrating_set__all')
).order_by(
	'min_session_date_from',
	'-avg_teacher_rating'
).filter(
	min_session_date_from__gte=datetime.now() - datetime.timedelta(days=240)
	avg_teacher_rating__lte=4
)

The Q is used to allow you to make logical AND and logical OR in the queries. 



class Blog(models.Model):
	name = models.CharField(max_length=100)
	tagline = models.TextField()

	def __unicode__(self):
		return self.name

class Author(models.Model):
	name = models.CharField(max_length=50)
	email = models.EmailField()

	def __unicode__(self):
		return self.name

class Entry(models.Model):
	blog = models.ForeignKey(Blog)
	headline = models.CharField(max_length=255)
	body_text = models.TextField()
	pub_date = models.DateField()
	mod_date = models.DateField()
	authors = models.ManyToManyField(Author)
	n_comments = models.IntegerField()
	n_pingbacks = models.IntegerField()
	rating = models.IntegerField()

	def __unicode__(self):
		return self.headline



author_blogs = Blog.objects.filter(entry__authors=author)






"""